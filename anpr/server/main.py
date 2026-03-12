import asyncio
import csv
import io
import logging
import re
from contextlib import asynccontextmanager
from datetime import date, datetime, timedelta
from logging.handlers import RotatingFileHandler

from bs4 import BeautifulSoup
from databases import Database
from fastapi import Body, Depends, FastAPI, Header, HTTPException, Path, Request
from fastapi.responses import StreamingResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
import pandas as pd
from pydantic import BaseModel, field_validator
import requests
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from uvicorn.logging import ColourizedFormatter

import config.config as config
import config.constance as constance
from data_models.attraction import Attraction
from data_models.attraction_comparison_chart import ATTRACTION_COMPARISON_CHART
from data_models.attraction_status import AttractionStatus
from data_models.entrance import Entrance
from data_models.error import Error
from data_models.waiting_time import WaitingTime

# 環境変数確認
if config.DATABASE_URL is None:
    raise ValueError("DATABASE_URL is not set")
else:
    database = Database(config.DATABASE_URL)

if config.API_KEY is None:
    raise ValueError("API_KEY is not set")
else:
    api_key = config.API_KEY

if config.API_NAME is None:
    raise ValueError("API_NAME is not set")  
else:
    api_name = config.API_NAME

# ログ設定
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

logger_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_formatter = ColourizedFormatter(
    fmt = "%(asctime)s - %(levelprefix)s - %(message)s",
    style = "%",
    use_colors = True
)

info_handler = RotatingFileHandler("info.log", maxBytes = 1024 * 1024 * 10, backupCount = 10)
info_handler.setLevel(logging.INFO)
info_handler.setFormatter(logger_formatter)

error_handler = RotatingFileHandler("error.log", maxBytes = 1024 * 1024 * 10, backupCount = 10)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logger_formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(console_formatter)

root_logger.addHandler(info_handler)
root_logger.addHandler(error_handler)
root_logger.addHandler(console_handler)

logging.getLogger("uvicorn").handlers = root_logger.handlers
logging.getLogger("uvicorn.access").handlers = root_logger.handlers

logger_info = logging.getLogger("uvicorn.info")
logger_error = logging.getLogger("uvicorn.error")

# 営業時間変形 (例: 09:00~17:00 -> 08:45~17:00)
async def transform_working_hours(working_hours: str) -> str:
    try:
        start_working_hour = working_hours.split("~")[0]
        end_working_hour = working_hours.split("~")[1]

        start_working_hour_dt = datetime.strptime(start_working_hour, "%H:%M")
        start_working_hour_dt -= timedelta(minutes = 15)
        start_working_hour = start_working_hour_dt.strftime("%H:%M")

        logger_info.info(f"[transform_working_hours] Successfully transformed working hours: ({working_hours} -> {start_working_hour}~{end_working_hour})")
        return f"{start_working_hour}~{end_working_hour}"
    except Exception as e:
        logger_error.error(f"[transform_working_hours] Failed to transform working hours: {e}")
        return "Error"

# 営業日チェック
async def check_open_or_closed(year: str, month: str, day: str, transform: bool = True) -> str:
    if  int(month) < 10:
        month = "0" + month

    try:
        logger_info.info(f"[check_open_or_closed] Checking if the park is open or closed: {year}/{month}/{day}")
        url = f"https://pal2.co.jp/fee/{year}/{month}/#calendar"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
        data = response.text

        soup = BeautifulSoup(data, "html.parser")
        table = soup.find("table")
        rows = table.find_all("tr")

        for row in rows:
            cols = row.find_all("td")
            
            for col in cols:
                if re.search("0", month):
                    month = month[1]

                rel = col.get("rel")
                regex = f"{month}/{day}$"

                if rel is not None and re.match(regex, rel):
                    if col.find("p", class_ = "rest") is not None:
                        logger_info.info("[check_open_or_closed] Successfully checked working day: Closed")
                        return "Closed"
                    else:
                        working_hours = col.find("a", class_ = "t_inner").get("data-time")
                        working_hours = working_hours.replace("～", "~")
                        
                        if working_hours[0] != "1" and working_hours[0] != "2":
                            working_hours = "0" + working_hours
                        
                        logger_info.info(f"[check_open_or_closed] Successfully checked working day: Open ({working_hours})")
                        if transform:
                            return await transform_working_hours(working_hours)
                        else:
                            return working_hours
        
    except Exception as e:
        logger_error.error(f"[check_open_or_closed] Failed to check working day: {e}")
        return "Error"

# 5分おきに待ち時間参照
async def refer_waiting_time() -> None:
    while True:
        try:
            start_processing_time = datetime.now()
            working_hours = await check_open_or_closed(year = str(datetime.now().year), month = str(datetime.now().month), day = str(datetime.now().day), transform = True)

            if working_hours != "Closed" and working_hours != "Error":
                start_working_hour = datetime.strptime(working_hours.split("~")[0], "%H:%M")
                end_working_hour = datetime.strptime(working_hours.split("~")[1], "%H:%M")

                start_working_hour = start_working_hour.time()
                end_working_hour = end_working_hour.time()
                current_hm = datetime.now().time()
                
                if start_working_hour <= current_hm <= end_working_hour:
                    logger_info.info("[refer_waiting_time] Started gathering waiting time schedules")
                    select_car_count_query = """
                        SELECT COUNT(*) FROM entrance WHERE timestamp >= CURDATE()
                    """

                    select_attraction_status_query = """
                        SELECT attraction_name, status FROM attraction_status WHERE attraction_name = :attraction_name ORDER BY timestamp DESC LIMIT 1
                    """

                    insert_query = """
                        INSERT INTO waiting_time (timestamp, attraction_name, waiting_time, attraction_status)
                        VALUES (:timestamp, :attraction_name, :waiting_time, :attraction_status)
                    """

                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    reference_list = {}
                    
                    try:
                        data = await database.fetch_all(select_car_count_query)
                        car_count = data[0]["COUNT(*)"]

                        logger_info.info(f"[refer_waiting_time] Car count retrieved: {car_count}")

                        if car_count < 50:
                            reference_list = constance.SCHEDULE_DATA_UNDER_FIFTY
                        elif car_count < 100:
                            reference_list = constance.SCHEDULE_DATA_UNDER_ONE_HUNDRED
                        elif car_count < 200:
                            reference_list = constance.SCHEDULE_DATA_UNDER_TWO_HUNDRED
                        elif car_count < 300:
                            reference_list = constance.SCHEDULE_DATA_UNDER_THREE_HUNDRED
                        elif car_count < 400:
                            reference_list = constance.SCHEDULE_DATA_UNDER_FOUR_HUNDRED
                        elif car_count < 500:
                            reference_list = constance.SCHEDULE_DATA_UNDER_FIVE_HUNDRED
                        elif car_count < 600:
                            reference_list = constance.SCHEDULE_DATA_UNDER_SIX_HUNDRED
                        elif car_count < 700:
                            reference_list = constance.SCHEDULE_DATA_UNDER_SEVEN_HUNDRED
                        elif car_count < 800:
                            reference_list = constance.SCHEDULE_DATA_UNDER_EIGHT_HUNDRED
                        else:
                            reference_list = constance.SCHEDULE_DATA_OVER_EIGHT_HUNDRED

                    except Exception as e:
                        logger_error.error(f"[refer_waiting_time] Failed to set reference schedule list: {e}")
                        
                    referred_attraction_count = 0
                    error_attractions_list = []

                    for attraction in Attraction:
                        try:
                            attraction_name = attraction.value
                            attraction_status_data = await database.fetch_one(select_attraction_status_query, values = {"attraction_name": attraction_name})
                            attraction_status = attraction_status_data.status
                            
                            schedules = reference_list.get(attraction, {})
                        except Exception as e:
                            logger_error.error(f"[refer_waiting_time] Failed to fetch status for {attraction_name if 'attraction_name' in locals() else attraction}: {e}")
                            if "attraction_name" in locals():
                                error_attractions_list.append(attraction_name)
                            continue
                        
                        for time_range, waiting_time in schedules.items():
                            try:
                                if attraction_name == Attraction.GO_CART.value:
                                    continue

                                start_hm = datetime.strptime(time_range.split("-")[0], "%H:%M")
                                end_hm = datetime.strptime(time_range.split("-")[1], "%H:%M")

                                if start_hm.time() <= current_hm and end_hm.time() >= current_hm:
                                    if attraction_status == config.ATTRACTION_STATUS_RUNNING:
                                        await database.execute(insert_query, values={"timestamp": timestamp, "attraction_name": attraction_name, "waiting_time": waiting_time, "attraction_status": attraction_status})
                                    else:
                                        await database.execute(insert_query, values={"timestamp": timestamp, "attraction_name": attraction_name, "waiting_time": config.ATTRACTION_WAITING_TIME_ERROR, "attraction_status": attraction_status})
                                        
                                    logger_info.info(f"[refer_waiting_time] Successfully inserted waiting time for {attraction_name}")
                                    referred_attraction_count += 1
                                    break
                            except Exception as e:
                                logger_error.error(f"[refer_waiting_time] Failed to insert waiting time for {attraction_name}: {e}")
                                error_attractions_list.append(attraction_name)
                                continue
                    
                    if error_attractions_list:
                        for error_attraction in error_attractions_list:
                            try:
                                attraction_status_data = await database.fetch_one(select_attraction_status_query, values = {"attraction_name": error_attraction})
                                await database.execute(insert_query, values={"timestamp": timestamp, "attraction_name": error_attraction, "waiting_time": config.ATTRACTION_WAITING_TIME_ERROR, "attraction_status": attraction_status_data.status})
                            except Exception as e:
                                logger_error.error(f"[refer_waiting_time] Failed to record fallback error state for {error_attraction}: {e}")
                        logger_error.error(f"[refer_waiting_time] Recorded fallback error state for attractions: {error_attractions_list}")
                    
                    logger_info.info(f"[refer_waiting_time] Successfully referred and saved waiting time for {referred_attraction_count} attractions")
                
            end_processing_time = datetime.now()
            total_processing_time = (end_processing_time - start_processing_time).total_seconds()
            await asyncio.sleep(max(0, 300 - total_processing_time))
        except Exception as e:
            logger_error.error(f"[refer_waiting_time] Unexpected error in main loop: {e}")
            await asyncio.sleep(60)

# DBライフサイクル
@asynccontextmanager
async def lifespan(app: FastAPI):
    FastAPICache.init(backend=InMemoryBackend(), prefix="fastapi-cache")
    logger_info.info("[lifespan] Successfully initialized FastAPI Cache")

    try:
        await database.connect()
        logger_info.info("[lifespan] Successfully connected to database")
    except Exception as e:
        logger_error.error(f"[lifespan] Failed to connect to database: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to connect to database: {e}") from e
    
    entrance_table_creation_query = """
                CREATE TABLE IF NOT EXISTS entrance (
                    id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    timestamp DATETIME NOT NULL,
                    region_code VARCHAR(16) NOT NULL,
                    INDEX idx_entrance (id, timestamp)
                );
    """
    
    try:
        await database.execute(entrance_table_creation_query)
        logger_info.info("[lifespan] Successfully created typical 'entrance' table")
    except Exception as e:
        logger_error.error(f"[lifespan] Failed to create 'entrance' table: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create 'entrance' table: {e}") from e

    error_table_creation_query = """
                CREATE TABLE IF NOT EXISTS error (
                    id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    timestamp DATETIME NOT NULL,
                    raspberry_pi_num VARCHAR(16) NOT NULL,
                    error_type VARCHAR(32) NOT NULL,
                    error VARCHAR(255) NOT NULL,
                    INDEX idx_error (id, timestamp, raspberry_pi_num, error_type, error)
                );
    """
    
    try:
        await database.execute(error_table_creation_query)
        logger_info.info("[lifespan] Successfully created 'error' table")
    except Exception as e:
        logger_error.error(f"[lifespan] Failed to create 'error' table: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create 'error' table: {e}") from e

    waiting_time_table_creation_query = """
                CREATE TABLE IF NOT EXISTS waiting_time (
                    id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    timestamp DATETIME NOT NULL,
                    attraction_name VARCHAR(32) NOT NULL,
                    waiting_time INT NOT NULL,
                    attraction_status VARCHAR(8) NOT NULL,
                    INDEX idx_waiting_time (id, timestamp, attraction_name, waiting_time, attraction_status)
                );
    """

    try:
        await database.execute(waiting_time_table_creation_query)
        logger_info.info("[lifespan] Successfully created 'waiting_time' table")
    except Exception as e:
        logger_error.error(f"[lifespan] Failed to create 'waiting_time' table: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create 'waiting_time' table: {e}") from e

    attraction_status_table_creation_query = """
                CREATE TABLE IF NOT EXISTS attraction_status (
                    id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    timestamp DATETIME NOT NULL,
                    attraction_name VARCHAR(32) NOT NULL,
                    status VARCHAR(8) NOT NULL,
                    INDEX idx_attraction_status (id, timestamp, attraction_name, status)
                );
    """

    try:
        await database.execute(attraction_status_table_creation_query)
        logger_info.info("[lifespan] Successfully created 'attraction_status' table")
    except Exception as e:
        logger_error.error(f"[lifespan] Failed to create 'attraction_status' table: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create 'attraction_status' table: {e}") from e

    try:
        bg_task = asyncio.create_task(refer_waiting_time())
        logger_info.info("[lifespan] Successfully created background schedule task")
    except Exception as e:
        logger_error.error(f"[lifespan] Failed to create background task: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create task: {e}") from e

    yield

    try:
        bg_task.cancel()
        logger_info.info("[lifespan] Successfully canceled background task")
        await database.disconnect()
        logger_info.info("[lifespan] Successfully disconnected from database")
    except Exception as e:
        logger_error.error(f"[lifespan] Error during shutdown: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to disconnect from database: {e}") from e

# SlowAPI初期化
limiter = Limiter(key_func = get_remote_address)

# FastAPIアプリケーション起動
app = FastAPI(lifespan = lifespan)

# Bearer認証スキームの定義
oauth2_scheme = HTTPBearer()

# SlowAPI初期化の続き
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# API認証
def authenticate_api_key(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    try:
        if credentials.credentials != api_key:
            raise HTTPException(status_code=401, detail="Invalid API Key")
        return True
    except HTTPException:
        raise
    except Exception as e:
        logger_error.error(f"[authenticate_api_key] Error validating API key: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

# APIエンドポイント
# API生存確認
@app.get("/api", status_code=200)
async def get_api_status(auth: bool = Depends(authenticate_api_key)):
    try:
        return {"message": "API is running"}
    except Exception as e:
        logger_error.error(f"[get_api_status] Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

# 入場記録
@app.post("/api/entrance", status_code=201)
async def record_entrance(items: Entrance | list[Entrance] = Body(...), auth: bool = Depends(authenticate_api_key)):
    try:
        insert_query = """
            INSERT INTO entrance (timestamp, region_code)
            VALUES (:timestamp, :region_code)
        """

        if isinstance(items, Entrance):
            items = [items]

        data = []
        error_data = []
        skipped_data = []

        logger_info.info("[record_entrance] Started recording data into entrance table")

        for item in items:
            if item.region_code == "":
                error_data.append({"timestamp": item.timestamp, "region_code": item.region_code})
                continue

            year = item.timestamp.year
            month = item.timestamp.month
            day = item.timestamp.day

            working_hours = await check_open_or_closed(year = str(year), month = str(month), day = str(day))

            if working_hours != "Closed" and working_hours != "Error":
                start_working_hour = datetime.strptime(working_hours.split("~")[0], "%H:%M")
                end_working_hour = datetime.strptime(working_hours.split("~")[1], "%H:%M")

                start_working_hour = start_working_hour.time()
                end_working_hour = end_working_hour.time()
                timestamp_hm = item.timestamp.time()
            
                if start_working_hour > timestamp_hm or end_working_hour < timestamp_hm:
                    logger_info.info(f"[record_entrance] Skipped entrance data (out of hours): {item.timestamp}, {item.region_code}")
                    skipped_data.append({"timestamp": item.timestamp, "region_code": item.region_code})
                elif working_hours == "Closed":
                    logger_info.info(f"[record_entrance] Skipped entrance data (closed day): {item.timestamp}, {item.region_code}")
                    skipped_data.append({"timestamp": item.timestamp, "region_code": item.region_code})
                elif working_hours == "Error":
                    logger_error.error(f"[record_entrance] Failed to check open or closed for data: {item.timestamp}, {item.region_code}")
                    error_data.append({"timestamp": item.timestamp, "region_code": item.region_code})
                else:
                    data.append({"timestamp": item.timestamp, "region_code": item.region_code})
                    # Use debug here if it produces too much noise, but info is fine given current implementation
                    logger_info.info(f"[record_entrance] Verified valid entrance data: {item.timestamp}, {item.region_code}")

        await database.execute_many(insert_query, values=data)
        logger_info.info("[record_entrance] Successfully recorded entrance data into table")
        
        return {"message": "Entrance data recorded successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger_error.error(f"[record_entrance] Failed to record entrance data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to record entrance data: {e}")

# 今日の入場記録数
@app.get("/api/entrance/count", status_code=200)
async def get_entrance_count(auth: bool = Depends(authenticate_api_key)):
    try:
        select_query = """
            SELECT COUNT(*) FROM entrance WHERE timestamp >= CURDATE()
        """

        working_hours = await check_open_or_closed(year = str(datetime.now().year), month = str(datetime.now().month), day = str(datetime.now().day))
        
        if working_hours == "Closed":
            raise HTTPException(status_code=422, detail="The park is closed today")
        
        if working_hours == "Error":
            raise HTTPException(status_code=500, detail="Failed to check open or closed")

        logger_info.info("[get_entrance_count] Started fetching today's entrance data")
        data = await database.fetch_all(select_query)
        data = data[0]["COUNT(*)"]
        logger_info.info("[get_entrance_count] Successfully fetched today's entrance data")
        return {"message": "Entrance data fetched successfully", "data": data}
    except HTTPException:
        raise
    except Exception as e:
        logger_error.error(f"[get_entrance_count] Failed to fetch count data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch data from entrance table: {e}")

# 指定日付の入場記録CSV
@app.get("/api/entrance/csv", status_code=200)
async def get_entrance_csv(date_from: date, date_to: date, auth: bool = Depends(authenticate_api_key)):
    # date_from: "2025-01-01", 
    # date_to: "2025-12-31"
    try:
        select_query = """
            SELECT timestamp, region_code FROM entrance WHERE DATE(timestamp) BETWEEN DATE(:date_from) AND DATE(:date_to)
        """

        if date_from > date_to:
            raise HTTPException(status_code=422, detail="Invalid date range")

        try:
            datetime.fromisoformat(str(date_from))
            datetime.fromisoformat(str(date_to))
        except ValueError:
            logger_error.error(f"[get_entrance_csv] Invalid date format provided: {date_from}, {date_to}")
            raise HTTPException(status_code=422, detail=f"Invalid date format: {date_from}, {date_to}")
        
        logger_info.info("[get_entrance_csv] Started fetching entrance data for CSV")
        data = await database.fetch_all(select_query, values={"date_from": date_from, "date_to": date_to})
        if len(data) == 0:
            logger_info.warning("[get_entrance_csv] No entrance data found for the specified range")
            return {"message": "Entrance data fetched successfully", "data": data}
        
        df = pd.DataFrame(dict(row) for row in data)
        stream = io.StringIO()
        df.to_csv(stream, index=False)
        stream.seek(0)
        response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
        response.headers["Content-Disposition"] = f"attachment; filename={date_from}_{date_to}.csv"
        logger_info.info("[get_entrance_csv] Successfully generated and fetched CSV data")
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger_error.error(f"[get_entrance_csv] Failed to fetch data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch data from entrance table: {e}")

# 今日の各地域の入場数
@app.get("/api/entrance/region_code", status_code=200)
async def get_today_region_code_from_entrance(auth: bool = Depends(authenticate_api_key)):
    try:
        select_query = """
            SELECT region_code, COUNT(*) as count FROM entrance WHERE timestamp >= CURDATE() GROUP BY region_code
        """

        working_hours = await check_open_or_closed(year = str(datetime.now().year), month = str(datetime.now().month), day = str(datetime.now().day))
        
        if working_hours == "Closed":
            raise HTTPException(status_code=422, detail="The park is closed today")
        
        if working_hours == "Error":
            raise HTTPException(status_code=500, detail="Failed to check open or closed")

        logger_info.info("[get_today_region_code_from_entrance] Started fetching region code data")
        region_code_list = constance.REGION_CODE_LIST        
        data = await database.fetch_all(select_query)

        if len(data) == 0:
            logger_info.warning("[get_today_region_code_from_entrance] No entrance data found today")
            return {"message": "No entrance data found", "data": []}
        data = {row["region_code"]: row["count"] for row in data}

        for item in data:
            if item not in region_code_list and item != config.UNDEFINED_TEXT:
                logger_error.error(f"[get_today_region_code_from_entrance] Invalid region code found in DB: {item}")
                raise HTTPException(status_code=422, detail="Invalid region code")

        logger_info.info("[get_today_region_code_from_entrance] Successfully fetched localized entry counts")
        return {"message": "Entrance data fetched successfully", "data": data}
    except HTTPException:
        raise
    except Exception as e:
        logger_error.error(f"[get_today_region_code_from_entrance] Failed to fetch region code data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch data from entrance table: {e}")

# エラー記録
@app.post("/api/error", status_code=201)
async def record_error(error: Error, auth: bool = Depends(authenticate_api_key)):
    try:
        insert_query = """
            INSERT INTO error (timestamp, raspberry_pi_num, error_type, error)
            VALUES (:timestamp, :raspberry_pi_num, :error_type, :error)
        """

        logger_info.info("[record_error] Started recording error data reported by device")
        await database.execute(insert_query, values={"timestamp": error.timestamp, "raspberry_pi_num": error.raspberry_pi_num, "error_type": error.error_type, "error": error.error})
        logger_info.info(f"[record_error] Successfully recorded error from pi_{error.raspberry_pi_num}")
        return {"message": "Error recorded successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger_error.error(f"[record_error] Failed to insert error data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to record error data into error table: {e}")

# 今日のエラー記録
@app.get("/api/error/status", status_code=200)
async def get_today_status_from_error(auth: bool = Depends(authenticate_api_key)):
    try:
        select_query = """
            SELECT timestamp, error_type, error, raspberry_pi_num FROM error WHERE timestamp >= CURDATE()
        """

        logger_info.info("[get_today_status_from_error] Started fetching today's error logs")
        data = await database.fetch_all(select_query)
        if len(data) == 0:
            logger_info.warning("[get_today_status_from_error] No error data found today")
            return {"message": "No error data found", "data": []}
        else:
            logger_info.info("[get_today_status_from_error] Successfully fetched error status logs")
            return {"message": "Error data fetched successfully", "data": data}
    except Exception as e:
        logger_error.error(f"[get_today_status_from_error] Failed to fetch error data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch data from error table: {e}")

# アトラクション運行状況
@app.post("/api/attraction_status", status_code=201)
async def record_attraction_status(items: AttractionStatus | list[AttractionStatus] = Body(...), auth: bool = Depends(authenticate_api_key)):
    try:
        timestamp = datetime.now().strftime(config.TIME_STAMP_FORMAT)
        insert_query = """
            INSERT INTO attraction_status (timestamp, attraction_name, status)
            VALUES (:timestamp, :attraction_name, :status)
        """

        if isinstance(items, AttractionStatus):
            items = [items]

        data = []
        error_data = []

        logger_info.info("[record_attraction_status] Started processing attraction status payloads")

        for item in items:
            item.buttonId = item.buttonId.replace("status-", "")

            if item.buttonId not in [attraction["attraction_name_local"] for attraction in ATTRACTION_COMPARISON_CHART]:
                logger_error.error(f"[record_attraction_status] Invalid attraction name parsed: {item.buttonId}")
                error_data.append({"timestamp": timestamp, "attraction_name": item.buttonId, "error": "Invalid attraction name"})
            
            if item.status not in ["運行", "点検", "休止", "雨天", "雷", "強風", "繰上", "悪天"]:
                logger_error.error(f"[record_attraction_status] Invalid attraction status parsed: {item.status} for {item.buttonId}")
                error_data.append({"timestamp": timestamp, "attraction_name": item.buttonId, "error": "Invalid attraction status"})
            
            for attraction in ATTRACTION_COMPARISON_CHART:
                if item.buttonId == attraction["attraction_name_local"]:
                    item.buttonId = attraction["attraction_name_server"]

                    if item.status == "運行":
                        item.status = config.ATTRACTION_STATUS_RUNNING
                    elif item.status == "点検":
                        item.status = config.ATTRACTION_STATUS_INSPECTION
                    elif item.status == "休止":
                        item.status = config.ATTRACTION_STATUS_SUSPENDED
                    elif item.status == "雨天":
                        item.status = config.ATTRACTION_STATUS_RAIN
                    elif item.status == "雷":
                        item.status = config.ATTRACTION_STATUS_THUNDER
                    elif item.status == "強風":
                        item.status = config.ATTRACTION_STATUS_STRONG_WIND
                    elif item.status == "繰上":
                        item.status = config.ATTRACTION_STATUS_EARLY_CLOSE
                    elif item.status == "悪天":
                        item.status = config.ATTRACTION_STATUS_BAD_WEATHER
                    
                    data.append({"timestamp": timestamp, "attraction_name": item.buttonId, "status": item.status})
                    logger_info.info(f"[record_attraction_status] Validated status change: {item.buttonId} -> {item.status}")
                    break
            
        await database.execute_many(query=insert_query, values=data)
        logger_info.info(f"[record_attraction_status] Successfully registered {len(data)} attraction status entries")

        if error_data:
            logger_error.error(f"[record_attraction_status] Completed with some invalid payloads: {error_data}")
            raise HTTPException(status_code=422, detail=f"Invalid attraction name or status: {error_data}") 

        return {"message": "Attraction status recorded successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger_error.error(f"[record_attraction_status] Unexpected failure while tracking status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to record data into attraction_status table: {e}")

@app.get("/api/attraction_status/status", status_code = 200)
async def get_attraction_status_status(auth: bool = Depends(authenticate_api_key)):
    try:
        select_query = """
            SELECT timestamp, attraction_name, status FROM attraction_status WHERE attraction_name = :attraction_name ORDER BY timestamp DESC LIMIT 1
        """

        data = []

        logger_info.info("[get_attraction_status_status] Started fetching latest attraction states")

        for attraction in ATTRACTION_COMPARISON_CHART:
            data.append(await database.fetch_one(select_query, values={"attraction_name": attraction["attraction_name_server"]}))

        if len(data) == 0:
            logger_info.warning("[get_attraction_status_status] No attraction status data available in DB")
            return {"message": "No attraction status data found", "data": []}
        else:
            logger_info.info("[get_attraction_status_status] Successfully fetched the latest attraction states")
            return {"message": "Attraction status data fetched successfully", "data": data}
    except Exception as e:
        logger_error.error(f"[get_attraction_status_status] Failed to retrieve statuses: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch data from attraction_status table: {e}")

# 現在の待ち時間
@app.get("/api/waiting_time", status_code = 200)
@limiter.limit("30/minute")
@cache(expire = 60)
async def get_waiting_time(request: Request):
    try:
        select_query = """
            SELECT timestamp, attraction_name, waiting_time, attraction_status FROM waiting_time WHERE timestamp = (SELECT MAX(timestamp) FROM waiting_time WHERE CAST(timestamp AS DATE) = CURRENT_DATE)
        """

        working_hours = await check_open_or_closed(year = str(datetime.now().year), month = str(datetime.now().month), day = str(datetime.now().day), transform = False)

        if working_hours == "Closed":
            raise HTTPException(status_code=422, detail="The park is closed today")
        
        if working_hours == "Error":
            raise HTTPException(status_code=500, detail="Failed to check open or closed")

        start_working_hour = datetime.strptime(working_hours.split("~")[0], "%H:%M")
        end_working_hour = datetime.strptime(working_hours.split("~")[1], "%H:%M")

        start_working_hour = start_working_hour.time()
        end_working_hour = end_working_hour.time()
        current_hm = datetime.now().time()
        
        if current_hm < start_working_hour or current_hm > end_working_hour:
            raise HTTPException(status_code=422, detail="The park is closed now")

        logger_info.info("[get_waiting_time] Started fetching latest waiting time data")
        data = await database.fetch_all(select_query)
        if len(data) == 0:
            logger_info.warning("[get_waiting_time] No waiting time data found today")
            return {"message": "No waiting time data found", "data": []}
        else:
            logger_info.info("[get_waiting_time] Successfully fetched waiting time data")
            return {"message": "Waiting time data fetched successfully", "data": data}
    except HTTPException:
        raise
    except Exception as e:
        logger_error.error(f"[get_waiting_time] Failed to fetch latest waiting time: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch latest waiting time data from waiting time table: {e}")
