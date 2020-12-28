from __future__ import annotations

from pathlib import Path
from typing import List

from fastapi import Header
from pydantic import BaseModel, validator


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


class UploadCreation(BaseModel):
    owner_id: str
    loid: int
    file_path: str

    class Config:
        orm_values = True


class UploadCreationHeaders(BaseModel):
    file_path: Path = Header(...)

    @validator('file_path')
    def must_be_not_empty(cls, v: Path) -> Path:
        path_parts: List[str] = str(v).split('/')
        if len(path_parts) < 2:
            raise ValueError('Each file must be put in at least one directory.')
        return v

    @classmethod
    def as_header(
            cls,
            file_path: Path = Header(
                ...,
                description='new file location',
                convert_underscores=True
            )
    ) -> UploadCreationHeaders:
        return cls(file_path=file_path)
