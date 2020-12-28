from __future__ import annotations

from datetime import datetime
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


class UploadCacheData(BaseModel):
    owner_id: str
    loid: int
    file_path: str
    creation_time: datetime = datetime.utcnow()

    class Config:
        orm_values = True


class UploadLocationData(BaseModel):
    location: str

    class Config:
        orm_mode = True


class UploadCreationHeaders(BaseModel):
    file_path: Path

    @validator('file_path')
    def must_contain_at_least_one_directory(cls, v: Path) -> Path:
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


class UploadFileHeaders(BaseModel):
    upload_offset: int

    class Config:
        orm_mode = True

    @classmethod
    def as_header(
            cls,
            upload_offset: int = Header(
                ...,
                description='Tells api at which point it should start writing data at.',
                convert_underscores=True
            )
    ) -> UploadFileHeaders:
        return cls(upload_offset=upload_offset)
