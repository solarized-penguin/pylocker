from __future__ import annotations

from databases import Database
from fastapi import Depends
from sqlalchemy.sql import Insert

from app.core import get_db
from app.core.database_schema import files_table
from app.schemas.files import FileRead
from app.security import UserInfo


class FilesRepository:
    """
    Provides interface that enables communication with
    'files' table.
    """

    bytes_in_mb = 1000000

    def __init__(self, db: Database) -> None:
        self._db = db

    async def create_file(
            self, loid: int, file_path: str, file_size: int, user_info: UserInfo
    ) -> FileRead:
        query: Insert = files_table.insert(
            {
                'oid': loid,
                'file_path': file_path,
                'file_size_bytes': file_size,
                'owner_id': user_info.id
            }
        ).returning(
            files_table.c.file_path,
            files_table.c.file_size_bytes
        )
        inserted_file = await self._db.execute(query)

        return FileRead(
            file_path=inserted_file['file_path'],
            file_size_mb=(inserted_file['file_size_bytes'] / self.bytes_in_mb)
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
