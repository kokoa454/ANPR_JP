from pydantic import BaseModel

class WaitingTime(BaseModel):
    # id: int (auto increment)
    timestamp: str
    attraction_name: str
    waiting_time: int
