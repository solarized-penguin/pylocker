from __future__ import annotations

from pathlib import Path

from fastapi import Header
from pydantic import BaseModel


class FileBase(BaseModel):
    file_path: Path

    class Config:
        orm_mode = True


class FileDb(FileBase):
    id: int
    oid: int
    owner_id: str
    file_size_bytes: int


class FileRead(FileBase):
    file_size_mb: float


class FileUploadHeaders(BaseModel):
    file_path: Path = Header(...)

    @classmethod
    def as_header(
            cls,
            file_path: Path = Header(
                ...,
                description='new file location',
                convert_underscores=True
            )
    ) -> FileUploadHeaders:
        return cls(file_path=file_path)
