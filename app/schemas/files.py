from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

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
    file_checksum: Optional[str] = None


class FileRead(FileBase):
    file_size_mb: float
    checksum: Optional[str] = None


class UploadCacheData(BaseModel):
    owner_id: str
    loid: int
    file_path: str
    creation_time: datetime = datetime.utcnow()

    class Config:
        orm_values = True


class UploadFilePath(BaseModel):
    file_path: Path

    @classmethod
    def as_header(
            cls,
            file_path: Path = Header(
                ...,
                description='new file location',
                convert_underscores=True
            )
    ) -> UploadFilePath:
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
