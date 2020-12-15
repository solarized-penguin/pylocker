from pydantic import BaseModel


class FileBase(BaseModel):
    file_path: str

    class Config:
        orm_mode = True


class FileDb(FileBase):
    id: int
    oid: int
    owner_id: str
    file_size_bytes: int


class FileRead(FileBase):
    owner: str
    file_size_mb: float
