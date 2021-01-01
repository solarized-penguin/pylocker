import hashlib
from datetime import datetime
from pathlib import Path
from time import time
from typing import List, Tuple
from uuid import uuid4

from databases import Database
from faker import Faker
from httpx import AsyncClient, Response
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
    FileDb(id=1, oid=10000, file_path=Path('/test_path/file_1'),
           owner_id=user_id_1.email, file_size_bytes=1000 * bytes_in_mb,
           file_checksum=str(uuid4())),
    FileDb(id=2, oid=10001, file_path=Path('/test_path/file_2'),
           owner_id=user_id_1.email, file_size_bytes=100 * bytes_in_mb,
           file_checksum=str(uuid4())),
    FileDb(id=3, oid=10002, file_path=Path('/test_path/file_3'),
           owner_id=user_id_2.email, file_size_bytes=5000 * bytes_in_mb,
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


def calculate_hash(text: bytes) -> str:
    md5_hash = hashlib.md5(text)
    return md5_hash.hexdigest()


faker: Faker = Faker('en_US')

test_content: bytes = ' '.join(faker.sentences(10)).encode('utf-8')
test_content_hash: str = calculate_hash(test_content)


async def insert_uploaded_data(db: Database, file: FileDb) -> None:
    query: Insert = files_table.insert(
        {
            'id': file.id,
            'oid': file.oid,
            'file_path': str(file.file_path),
            'file_size_bytes': file.file_size_bytes,
            'owner_id': file.owner_id,
            'file_checksum': file.file_checksum
        }
    )
    await db.execute(query)


async def upload_file(aclient: AsyncClient, confirm_upload: bool) -> Tuple[str, str]:
    file_path: str = '/test_directory/test_file'

    response: Response = await aclient.post(
        '/resumable/files',
        headers={
            'file-path': file_path
        }
    )

    location: str = response.headers.get('location')

    await aclient.patch(
        '/resumable/files',
        files={'chunk': test_content},
        params={'location': location},
        headers={'upload-offset': '0'}
    )

    if confirm_upload:
        await aclient.post(
            '/resumable/files/confirm',
            params={
                'location': location,
                'checksum': test_content_hash
            }
        )

    return file_path, location
