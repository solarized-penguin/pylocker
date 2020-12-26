from databases import Database

from app.schemas.files import FileRead
from app.security import UserInfo


class FilesDao:
    def __init__(self, db: Database) -> None:
        self._db = db

    def create_file(self, loid: int, user_info: UserInfo) -> FileRead:
        pass
