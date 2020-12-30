from datetime import datetime
from pathlib import Path
from time import time
from typing import List
from uuid import uuid4

from databases import Database
from sqlalchemy.sql import Insert

from app.core.database_schema import files_table
from app.schemas.enums import UsernameStatus, TwoFactorDelivery
from app.schemas.files import FileDb
from app.schemas.users import UserInfo

bytes_in_mb = 1000000

user_id_1 = UserInfo(
    id='user_id_1', email='user1@test.com', active=True, passwordLastUpdateInstant=datetime.now(),
    usernameStatus=UsernameStatus.ACTIVE, twoFactorDelivery=TwoFactorDelivery.NONE,
    verified=True, tenantId='test_tenant', passwordChangeRequired=False, insertInstant=time()
)
user_id_2 = UserInfo(
    id='user_id_2', email='user2@test.com', active=True, passwordLastUpdateInstant=datetime.now(),
    usernameStatus=UsernameStatus.ACTIVE, twoFactorDelivery=TwoFactorDelivery.NONE,
    verified=True, tenantId='test_tenant', passwordChangeRequired=False, insertInstant=time()
)
user_id_3 = UserInfo(
    id='user_id_3', email='user3@test.com', active=True, passwordLastUpdateInstant=datetime.now(),
    usernameStatus=UsernameStatus.ACTIVE, twoFactorDelivery=TwoFactorDelivery.NONE,
    verified=True, tenantId='test_tenant', passwordChangeRequired=False, insertInstant=time()
)

test_files: List[FileDb] = [
    FileDb(id=1, oid=10000, file_path=Path('test_path/file_1'),
           owner_id=user_id_1.id, file_size_bytes=1000 * bytes_in_mb,
           file_checksum=str(uuid4())),
    FileDb(id=2, oid=10001, file_path=Path('test_path/file_2'),
           owner_id=user_id_1.id, file_size_bytes=100 * bytes_in_mb,
           file_checksum=str(uuid4())),
    FileDb(id=3, oid=10002, file_path=Path('test_path/file_3'),
           owner_id=user_id_2.id, file_size_bytes=5000 * bytes_in_mb,
           file_checksum=str(uuid4()))
]


async def insert_test_data(db: Database) -> None:
    for data in test_files:
        query: Insert = files_table.insert(
            {
                'id': data.id,
                'oid': data.oid,
                'file_path': str(data.file_path),
                'file_size_bytes': data.file_size_bytes,
                'owner_id': data.owner_id,
                'file_checksum': data.file_checksum
            }
        )
        await db.execute(query)
