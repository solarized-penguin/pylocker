import hashlib
from pathlib import Path
from typing import AsyncGenerator, Tuple

import pytest
from aredis import StrictRedis
from assertpy import assert_that
from databases import Database
from faker import Faker
from fastapi import FastAPI
from httpx import AsyncClient, Response
from sqlalchemy.sql import Insert, Select

from app import create_app
from app.auth_client import logged_user
from app.core import get_db, get_redis, Settings
from app.core.database_schema import files_table
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
    file_path: str = 'test_directory/test_file'

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


class TestDownloadFile:

    @pytest.mark.asyncio
    async def test__file_exists__returns_requested_data(
            self, aclient: AsyncClient, db: Database
    ) -> None:
        async with db.transaction(force_rollback=True):
            file_path, location = await upload_file(aclient, True)

            response: Response = await aclient.get(
                '/resumable/files',
                params={
                    'file_path': file_path,
                    'upload_offset': 0
                }
            )

            result: str = response.json()

            assert_that(result).is_equal_to(test_content.decode('utf-8'))

    @pytest.mark.asyncio
    async def test__file_does_not_exists__returns_404(
            self, aclient: AsyncClient
    ) -> None:
        response: Response = await aclient.get(
            '/resumable/files',
            params={
                'file_path': 'non_existing_path/file',
                'upload_offset': 0
            }
        )

        assert_that(response.status_code).is_equal_to(404)

    @pytest.mark.asyncio
    async def test__accessing_file_of_other_user__returns_403(
            self, aclient: AsyncClient, db: Database
    ) -> None:
        async with db.transaction(force_rollback=True):
            await insert_test_data(db)
            response: Response = await aclient.get(
                '/resumable/files',
                params={
                    'file_path': str(test_files[2].file_path),
                    'upload_offset': 0
                }
            )

            assert_that(response.status_code).is_equal_to(403)


class TestCreateNewUpload:

    @pytest.mark.asyncio
    async def test__file_path_header_passed_correctly__returns_location_header(
            self, aclient: AsyncClient
    ) -> None:
        response: Response = await aclient.post(
            '/resumable/files',
            headers={
                'file-path': 'test_directory/test_file.txt'
            }
        )

        result: str = response.headers.get('location')

        assert_that(result).is_not_empty()


class TestUploadFile:

    @pytest.mark.asyncio
    async def test__all_data_passed_correctly__returns_upload_offset(
            self, aclient: AsyncClient, db: Database
    ) -> None:
        async with db.transaction(force_rollback=True):
            file_path: str = 'test_directory/test_file'

            response: Response = await aclient.post(
                '/resumable/files',
                headers={
                    'file-path': file_path
                }
            )

            location: str = response.headers.get('location')

            response = await aclient.patch(
                '/resumable/files',
                files={'chunk': test_content},
                params={'location': location},
                headers={'upload-offset': '0'}
            )

            upload_offset: int = int(response.headers.get('upload-offset'))

            assert_that(upload_offset).is_equal_to(len(test_content))

    @pytest.mark.asyncio
    async def test__incorrect_location__returns_404(
            self, aclient: AsyncClient
    ) -> None:
        response = await aclient.patch(
            '/resumable/files',
            files={'chunk': test_content},
            params={'location': 'fake-location'},
            headers={'upload-offset': '0'}
        )

        assert_that(response.status_code).is_equal_to(404)

    @pytest.mark.asyncio
    async def test__upload_offset_header_not_present__returns_422(
            self, aclient: AsyncClient
    ) -> None:
        response = await aclient.patch(
            '/resumable/files',
            files={'chunk': test_content},
            params={'location': 'fake-location'}
        )

        assert_that(response.status_code).is_equal_to(422)


class TestConfirmUpload:

    @pytest.mark.asyncio
    async def test__data_passed_correctly__returns_confirmed_file(
            self, aclient: AsyncClient, db: Database
    ) -> None:
        async with db.transaction(force_rollback=True):
            file_path: str = 'test_directory/test_file'

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

            expected_result: FileRead = FileRead(
                file_path=Path(file_path),
                file_size_mb=(len(test_content) / bytes_in_mb),
                checksum=test_content_hash
            )

            response = await aclient.post(
                '/resumable/files/confirm',
                params={
                    'location': location,
                    'checksum': test_content_hash
                }
            )

            result: FileRead = FileRead.parse_obj(response.json())

            assert_that(result).is_equal_to(expected_result)


class TestFetchUploadOffset:

    @pytest.mark.asyncio
    async def test__correct_location__returns_offset(
            self, aclient: AsyncClient, db: Database
    ) -> None:
        async with db.transaction(force_rollback=True):
            file_path, location = await upload_file(aclient, False)

            response = await aclient.head(
                '/resumable/files',
                params={
                    'location': location
                }
            )

            result: int = int(response.headers.get('upload-offset'))

            assert_that(result).is_equal_to(len(test_content))

    @pytest.mark.asyncio
    async def test__location_does_not_exists__returns_404(
            self, aclient: AsyncClient
    ) -> None:
        response = await aclient.head(
            '/resumable/files',
            params={
                'location': 'fake-location'
            }
        )

        assert_that(response.status_code).is_equal_to(404)


class TestDeleteFile:

    @pytest.mark.asyncio
    async def test__file_exists__deletes_file(
            self, aclient: AsyncClient, db: Database
    ) -> None:
        async with db.transaction(force_rollback=True):
            file_path, location = await upload_file(aclient, True)

            await aclient.delete(
                '/resumable/files',
                params={
                    'file_path': file_path
                }
            )

            query: Select = files_table.select(files_table.c.file_path == file_path)

            result: None = await db.fetch_one(query)

            assert_that(result).is_none()

    @pytest.mark.asyncio
    async def test__file_does_not_exists__returns_404(
            self, aclient: AsyncClient, db: Database
    ) -> None:
        async with db.transaction(force_rollback=True):
            response: Response = await aclient.delete(
                '/resumable/files',
                params={
                    'file_path': 'fake/path'
                }
            )

            assert_that(response.status_code).is_equal_to(404)

    @pytest.mark.asyncio
    async def test__file_belongs_to_other_user__returns_403(
            self, aclient: AsyncClient, db: Database
    ) -> None:
        async with db.transaction(force_rollback=True):
            await insert_test_data(db)

            response: Response = await aclient.delete(
                '/resumable/files',
                params={
                    'file_path': str(test_files[2].file_path)
                }
            )

            assert_that(response.status_code).is_equal_to(403)
