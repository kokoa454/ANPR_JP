from pydantic import BaseModel

class AttractionStatus(BaseModel):
    buttonId: str
    status: str
