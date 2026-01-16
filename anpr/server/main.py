import config.config as config
import config.constance as constance
from data_models.entrance import Entrance
from data_models.error import Error
from databases import Database
from fastapi import FastAPI, Header, HTTPException, Body ,Path, Depends
from pydantic import BaseModel, field_validator
from contextlib import asynccontextmanager
from datetime import datetime
import io 
from fastapi.responses import StreamingResponse
import csv
import pandas as pd
from datetime import date
from data_models.waiting_time import WaitingTime
from data_models.attraction import Attraction
import requests
from bs4 import BeautifulSoup
import re

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

# DBライフサイクル
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await database.connect()
        print("DB接続完了")
    except Exception as e:
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create entrance table: {e}") from e

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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create error table: {e}") from e

    waiting_time_table_creation_query = """
                CREATE TABLE IF NOT EXISTS waiting_time (
                    id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    timestamp DATETIME NOT NULL,
                    attraction_name VARCHAR(32) NOT NULL,
                    waiting_time INT NOT NULL,
                    INDEX idx_waiting_time (id, timestamp, attraction_name, waiting_time)
                );
    """

    try:
        await database.execute(waiting_time_table_creation_query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create waiting_time table: {e}") from e

    yield

    try:
        await database.disconnect()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to disconnect from database: {e}") from e

# API認証
def authenticate_api_key(user_api_key: str = Header(None, alias=api_name)):
    if user_api_key != api_key:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return True

# FastAPIアプリケーション起動
app = FastAPI(lifespan=lifespan)

# 営業日チェック
def check_open_or_closed() -> str:
    year = str(datetime.now().year)
    month = str(datetime.now().month)
    if  int(month) < 10:
        month = "0" + month
    day = str(datetime.now().day)

    url = f"https://pal2.co.jp/fee/{year}/{month}/#calendar"
    response = requests.get(url)
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
                    return "休業日"
                else:
                    working_hours = col.find("a", class_ = "t_inner").get("data-time")
                    working_hours = working_hours.replace("ï½", "~")
                    return "営業時間: " + working_hours

# APIエンドポイント
# 入場記録
@app.post("/api/entrance", status_code=201)
async def record_entrance(items: Entrance | list[Entrance] = Body(...), auth: bool = Depends(authenticate_api_key)):
    insert_query = """
        INSERT INTO entrance (timestamp, region_code)
        VALUES (:timestamp, :region_code)
    """

    if isinstance(items, Entrance):
        items = [items]

    data = []

    if check_open_or_closed() == "休業日":
        return {"message": "Entrance data not recorded due to the park is closed today"}

    try:
        for item in items:
            # timestamp_pattern = "%Y-%m-%d_%H:%M:%S"
            item.timestamp = item.timestamp.replace("_", " ")
            data.append({"timestamp": item.timestamp, "region_code": item.region_code})

        await database.execute_many(insert_query, values=data)
        return {"message": "Entrance data recorded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record data into entrance table: {e}")

# 今日の入場記録数
@app.get("/api/entrance/count", status_code=200)
async def get_entrance(auth: bool = Depends(authenticate_api_key)):
    select_query = """
        SELECT COUNT(*) FROM entrance WHERE DATE(timestamp) = DATE(NOW())
    """

    if check_open_or_closed() == "休業日":
        raise HTTPException(status_code=401, detail="The park is closed today")

    try:
        data = await database.fetch_all(select_query)
        data = data[0]["COUNT(*)"]
        return {"message": "Entrance data fetched successfully", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch data from entrance table: {e}")

# 指定日付の入場記録CSV
@app.get("/api/entrance/csv", status_code=200)
async def get_entrance(date_from: date, date_to: date, auth: bool = Depends(authenticate_api_key)):
    # date_from: "2025-01-01", 
    # date_to: "2025-12-31"
    
    select_query = """
        SELECT * FROM entrance WHERE DATE(timestamp) BETWEEN DATE(:date_from) AND DATE(:date_to)
    """
    
    try:
        data = await database.fetch_all(select_query, values={"date_from": date_from, "date_to": date_to})
        if len(data) == 0:
            raise HTTPException(status_code=404, detail="No data found")
        
        df = pd.DataFrame(dict(row) for row in data)
        stream = io.StringIO()
        df.to_csv(stream, index=False)
        stream.seek(0)
        response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
        response.headers["Content-Disposition"] = f"attachment; filename={date_from}_{date_to}.csv"
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch data from entrance table: {e}")

# 今日の各地域の入場数
@app.get("/api/entrance/region_code", status_code=200)
async def get_today_region_code_from_entrance(auth: bool = Depends(authenticate_api_key)):
    select_query = """
        SELECT region_code, COUNT(*) as count FROM entrance WHERE DATE(timestamp) = DATE(NOW()) GROUP BY region_code
    """

    if check_open_or_closed() == "休業日":
        raise HTTPException(status_code=401, detail="The park is closed today")

    try:
        region_code_list = constance.REGION_CODE_LIST        
        data = await database.fetch_all(select_query)
        data = {row["region_code"]: row["count"] for row in data}
        
        if len(data) == 0:
            return {"message": "Entrance data fetched successfully", "data": []}

        for item in data:
            if item not in region_code_list:
                raise HTTPException(status_code=500, detail="Invalid region code")

        return {"message": "Entrance data fetched successfully", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch data from entrance table: {e}")

# エラー記録
@app.post("/api/error", status_code=201)
async def record_error(error: Error, auth: bool = Depends(authenticate_api_key)):
    insert_query = """
        INSERT INTO error (timestamp, raspberry_pi_num, error_type, error)
        VALUES (:timestamp, :raspberry_pi_num, :error_type, :error)
    """

    try:
        error.timestamp = error.timestamp.replace("_", " ")
        await database.execute(insert_query, values={"timestamp": error.timestamp, "raspberry_pi_num": error.raspberry_pi_num, "error_type": error.error_type, "error": error.error})
        return {"message": "Error recorded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record data into error table: {e}")

# 今日のエラー記録
@app.get("/api/error/status", status_code=200)
async def get_today_status_from_error(auth: bool = Depends(authenticate_api_key)):
    select_query = """
        SELECT * FROM error WHERE DATE(timestamp) = DATE(NOW())
    """

    try:
        data = await database.fetch_all(select_query)
        if len(data) == 0:
            return {"message": "No error data found", "data": []}
        else:
            return {"message": "Error data fetched successfully", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch data from error table: {e}")
