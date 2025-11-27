from fastapi import FastAPI, Header, HTTPException
import config

app = FastAPI()

@app.get("/api/connectionCheck")
def connection_check(api_key: str = Header(None, alias=config.API_NAME)):
    if api_key != config.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    print("Connection Check: OK")
    return {"status": "OK"}

@app.post("/api/enteredVisitorsTable1")
def entered_visitors_table_1(data: dict, api_key: str = Header(None, alias=config.API_NAME)):
    if api_key != config.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    print("Entered Visitors Table 1:", data)
    return {"status": "OK"}

@app.post("/api/enteredVisitorsTable2")
def getDataForEnteredVisitorsTable2(data: dict, api_key: str = Header(None, alias=config.API_NAME)):
    if api_key != config.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    print("Entered Visitors Table 2:", data)
    return {"status": "OK"}

@app.post("/api/exitedVisitorsTable")
def getDataForExitedVisitorsTable(data: dict, api_key: str = Header(None, alias=config.API_NAME)):
    if api_key != config.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    print("Exited Visitors Table:", data)
    return {"status": "OK"}

@app.post("/api/regionCodeTable")
def getDataForRegionCodeTable(data: dict, api_key: str = Header(None, alias=config.API_NAME)):
    if api_key != config.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    print("Region Code Table:", data)
    return {"status": "OK"}
