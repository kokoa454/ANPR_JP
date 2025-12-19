from pydantic import BaseModel


class GetCSVFromEntrance(BaseModel):
    date_from: str
    date_to: str
