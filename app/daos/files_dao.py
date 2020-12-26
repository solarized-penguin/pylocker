from __future__ import annotations

from databases import Database
from fastapi import Depends

from app.core import get_db
from app.schemas.files import FileRead
from app.security import UserInfo


class FilesDao:
    """
    Provides interface that enables communication with
    'files' table.
    """

    def __init__(self, db: Database) -> None:
        self._db = db

    async def create_file(
            self, loid: int, file_path: str, file_size: int, user_info: UserInfo
    ) -> FileRead:
        pass

    @classmethod
    def create_dao(
            self, db_pool: Database = Depends(get_db)
    ) -> FilesDao:
        """
        Creates new instance of self.
        :param db_pool: database connection pool
        :return: instance of FilesDao
        :rtype: FilesDao
        """
        return FilesDao(db_pool)
