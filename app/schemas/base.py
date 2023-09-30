from pydantic import BaseModel


class DBBase(BaseModel):
    class Config:
        orm_mode = True
