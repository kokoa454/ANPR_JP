from pydantic import BaseModel

class Entrance(BaseModel):
    # id: int (auto increment)
    timestamp: str
    region_code: str
