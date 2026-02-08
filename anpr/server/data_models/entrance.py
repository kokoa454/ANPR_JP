from pydantic import BaseModel

class Entrance(BaseModel):
    timestamp: str
    region_code: str
