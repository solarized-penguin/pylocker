import hashlib
from typing import List, AsyncGenerator

import pytest
from aredis import StrictRedis
from assertpy import assert_that
from databases import Database
from faker import Faker
from fastapi import FastAPI
from httpx import AsyncClient, Response
from sqlalchemy.sql import Insert

from app import create_app
from app.auth_client import logged_user
from app.core import get_db, get_redis, Settings
from app.core.database_schema import files_table
from app.repositories.blob_repository import BlobRepository
from app.schemas.files import FileRead, FileDb
from app.schemas.users import UserInfo
from tests.utils.shared_mock_data import insert_test_data, user_id_1, bytes_in_mb, test_files

settings: Settings = Settings.get()


@pytest.mark.asyncio
@pytest.fixture(scope='function')
async def aclient(
        db: Database, redis: StrictRedis
) -> AsyncGenerator[AsyncClient, None]:
    app: FastAPI = create_app()

    def _get_db() -> Database: return db

    def _get_redis() -> StrictRedis: return redis

    def _logged_user() -> UserInfo: return user_id_1

    app.dependency_overrides[get_db] = _get_db
    app.dependency_overrides[get_redis] = _get_redis
    app.dependency_overrides[logged_user] = _logged_user

    aclient: AsyncClient = AsyncClient(app=app, base_url='http://testserver')
    yield aclient
    await aclient.aclose()


def calculate_hash(text: bytes) -> str:
    md5_hash = hashlib.md5(text)
    return md5_hash.hexdigest()


faker: Faker = Faker('en_US')

test_file: FileDb = test_files[0]
test_content: bytes = ' '.join(faker.sentences(50)).encode('utf-8')
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


async def upload_test_file(db: Database) -> None:
    blob_repository: BlobRepository = BlobRepository.create(db)

    loid: int = await blob_repository.create_blob()
    test_file.oid = loid
    test_file.file_checksum = test_content_hash

    await insert_uploaded_data(db, test_file)
    await blob_repository.write_to_blob(test_file.oid, 0, test_content)


class TestFetchUserFiles:

    @pytest.mark.asyncio
    async def test__user_has_files__returns_list_of_files(
            self, aclient: AsyncClient, db: Database
    ) -> None:
        async with db.transaction(force_rollback=True):
            await insert_test_data(db)

            expected_result: List[FileRead] = [FileRead(
                file_path=str(file.file_path),
                file_size_mb=file.file_size_bytes / bytes_in_mb,
                checksum=file.file_checksum
            ) for file in test_files if file.owner_id == user_id_1.id]

            response: Response = await aclient.get('/resumable/files/all')

            result: List[FileRead] = [FileRead.parse_obj(file) for file in response.json()]

            assert_that(result).is_equal_to(expected_result)

    @pytest.mark.asyncio
    async def test__user_has_no_files__returns_204(
            self, aclient: AsyncClient
    ) -> None:
        response: Response = await aclient.get('/resumable/files/all')

        assert_that(response.status_code).is_equal_to(204)


class TestDownloadFile:

    @pytest.mark.asyncio
    async def test__works_correctly__returns_requested_data(
            self, aclient: AsyncClient, db: Database
    ) -> None:
        async with db.transaction(force_rollback=True):
            await upload_test_file(db)

            response: Response = await aclient.get(
                '/resumable/files',
                params={
                    'file_path': str(test_file.file_path),
                    'upload_offset': 0
                }
            )

            result: str = response.json()

            assert_that(result).is_equal_to(test_content.decode('utf-8'))
