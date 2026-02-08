from pydantic import BaseModel

class Error(BaseModel):
    timestamp: str
    raspberry_pi_num: str
    error_type: str
    error: str
