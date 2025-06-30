from pydantic import BaseModel

class LogBase(BaseModel):
    message: str

class LogCreate(LogBase):
    pass

class Log(LogBase):
    id: int

    class Config:
        orm_mode = True
