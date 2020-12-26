from __future__ import annotations

from databases import Database
from fastapi import Depends

from app.core import get_db
from app.daos.queries.blob_queries import create_empty_blob, write_data_to_blob, \
    read_data_from_blob, delete_blob, get_size_of_blob, get_size_of_blob_function


class BlobDao:
    """
    Provides interface that enables communication with
    postgres large objects(BLOBs).
    """

    def __init__(self, db_pool: Database) -> None:
        self._db = db_pool

    async def create_blob(self) -> int:
        oid: int = await self._db.execute(create_empty_blob)
        return oid

    async def write_to_blob(
            self, loid: int, offset: int, data: bytes
    ) -> None:
        await self._db.execute(
            write_data_to_blob,
            {
                'loid': loid,
                'offset': offset,
                'data': data
            }
        )

    async def read_from_blob(
            self, loid: int, offset: int, length: int
    ) -> bytes:
        blob_chunk: bytes = await self._db.execute(
            read_data_from_blob,
            {
                'loid': loid,
                'offset': offset,
                'length': length
            }
        )
        return blob_chunk

    async def remove_blob(self, loid: int) -> bool:
        await self._db.execute(
            delete_blob,
            {
                'loid': loid
            }
        )
        return True

    async def get_last_byte(self, loid: int) -> int:
        async with self._db.transaction():
            await self._db.execute(get_size_of_blob_function)
            file_size: int = await self._db.execute(
                get_size_of_blob,
                {
                    'loid': loid
                }
            )
            return file_size

    @classmethod
    def create_dao(
            cls, db_pool: Database = Depends(get_db)
    ) -> BlobDao:
        """
        Creates new instance of self.
        :param db_pool: database connection pool
        :return: instance of BlobDao
        :rtype: BlobDao
        """
        return BlobDao(db_pool)
