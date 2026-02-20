from pydantic import BaseModel
from datetime import datetime

class Error(BaseModel):
    timestamp: datetime
    raspberry_pi_num: str
    error_type: str
    error: str
