from databases import Database
from fastapi import Depends

from ..core import get_db


class BlobManager:
    """
    Provides interface that enables communication with
    postgres large objects(BLOBs).
    """

    def __init__(
            self,
            db_pool: Database = Depends(get_db)
    ) -> None:
        self._db = db_pool

    def create_blob(self):
        pass
