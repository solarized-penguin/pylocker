from pydantic import BaseModel


class Message(BaseModel):
    message: str

    class Config:
        orm_mode = True
