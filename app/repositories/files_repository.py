from __future__ import annotations

from pathlib import Path
from typing import Optional, Mapping, Any, List

from databases import Database
from fastapi import Depends
from sqlalchemy.sql import Insert, Select, Delete, Update

from app.core import get_db
from app.core.database_schema import files_table
from app.errors import FileDoesNotExistsError
from app.schemas.files import FileRead, FileDb
from app.security import UserInfo


class FilesRepository:
    """
    Provides interface that enables communication with
    'files' table.
    """

    bytes_in_mb = 1000000

    def __init__(self, db: Database) -> None:
        self._db = db

    async def fetch_all_user_files(self, user_info: UserInfo) -> List[FileRead]:
        query: Select = files_table.select(files_table.c.owner_id == user_info.id)

        mappings: List[Mapping[str, Any]] = await self._db.fetch_all(query)

        return [FileRead(
            file_path=Path(mapping['file_path']),
            file_size_mb=(mapping['file_size_bytes'] / self.bytes_in_mb),
            checksum=mapping['file_checksum']
        ) for mapping in mappings]

    async def update_file(self, loid: int, params: FileDb) -> None:
        query: Update = files_table.update(
            whereclause=files_table.c.oid == loid,
            values=params.dict(exclude_unset=True)
        )

        await self._db.execute(query)

    async def delete_file(self, loid: int) -> None:
        query: Delete = files_table.delete(files_table.c.oid == loid)
        await self._db.execute(query)

    async def fetch_db_file(self, file_path: str) -> FileDb:
        query: Select = files_table.select(files_table.c.file_path == file_path)

        result: Optional[Mapping[str, Any]] = await self._db.fetch_one(query)

        if not result:
            raise FileDoesNotExistsError()

        return FileDb.parse_obj(result)

    async def create_file(
            self, loid: int, file_path: str, file_size: int,
            checksum: str, user_info: UserInfo
    ) -> FileRead:
        query: Insert = files_table.insert(
            {
                'oid': loid,
                'file_path': file_path,
                'file_size_bytes': file_size,
                'owner_id': user_info.id,
                'file_checksum': checksum
            }
        )

        await self._db.execute(query)

        return FileRead(
            file_path=Path(file_path),
            file_size_mb=(file_size / self.bytes_in_mb),
            checksum=checksum
        )

    @classmethod
    def create(
            cls, db_pool: Database = Depends(get_db)
    ) -> FilesRepository:
        """
        Creates new instance of self.
        :param db_pool: database connection pool
        :return: instance of FilesRepository
        :rtype: FilesRepository
        """
        return FilesRepository(db_pool)
