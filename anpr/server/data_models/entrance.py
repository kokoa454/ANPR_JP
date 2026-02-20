from pydantic import BaseModel
from datetime import datetime

class Entrance(BaseModel):
    timestamp: datetime
    region_code: str
