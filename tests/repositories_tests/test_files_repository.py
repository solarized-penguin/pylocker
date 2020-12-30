from datetime import datetime
from pathlib import Path
from time import time
from typing import List, Tuple, Dict, Any
from uuid import uuid4

import pytest
from assertpy import assert_that
from databases import Database
from sqlalchemy.sql import Insert, Select

from app.core.database_schema import files_table
from app.errors import FileDoesNotExistsError
from app.repositories.files_repository import FilesRepository
from app.schemas.enums import UsernameStatus, TwoFactorDelivery
from app.schemas.files import FileDb, FileRead
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


@pytest.fixture(scope='function')
def files_repository(db: Database) -> FilesRepository:
    return FilesRepository.create(db)


class TestFetchAllUserFiles:
    test_data: List[Tuple[UserInfo, List[FileRead]]] = [
        (user_id_1, [FileRead(
            file_path=file.file_path,
            file_size_mb=(file.file_size_bytes / bytes_in_mb),
            checksum=file.file_checksum
        ) for file in test_files if file.owner_id == user_id_1.id]),
        (user_id_2, [FileRead(
            file_path=file.file_path,
            file_size_mb=(file.file_size_bytes / bytes_in_mb),
            checksum=file.file_checksum
        ) for file in test_files if file.owner_id == user_id_2.id])
    ]

    @pytest.mark.parametrize('user_info,expected_result', test_data)
    @pytest.mark.asyncio
    async def test__user_has_files__returns_list_of_files(
            self, files_repository: FilesRepository, db: Database,
            user_info: UserInfo, expected_result: List[FileRead]
    ) -> None:
        async with db.transaction(force_rollback=True):
            await insert_test_data(db)

            result: List[FileRead] = await files_repository \
                .fetch_all_user_files(user_info)

            assert_that(result).is_equal_to(expected_result)

    @pytest.mark.asyncio
    async def test__user_has_no_files__returns_empty_list(
            self, files_repository: FilesRepository, db: Database
    ) -> None:
        async with db.transaction(force_rollback=True):
            result: List[FileRead] = await files_repository \
                .fetch_all_user_files(user_id_3)

            assert_that(result).is_equal_to([])


class TestDeleteFile:

    @pytest.mark.asyncio
    async def test__file_exists__deletes_file(
            self, files_repository: FilesRepository, db: Database
    ) -> None:
        async with db.transaction(force_rollback=True):
            await insert_test_data(db)

            test_oid: int = test_files[0].oid

            await files_repository.delete_file(test_oid)

            query: Select = files_table.select(files_table.c.oid == test_oid)

            result = await db.fetch_one(query)

            assert_that(result).is_none()


class TestFetchDbFile:

    @pytest.mark.asyncio
    async def test__file_exists__returns_file(
            self, files_repository: FilesRepository, db: Database
    ) -> None:
        async with db.transaction(force_rollback=True):
            await insert_test_data(db)

            expected_result: FileDb = test_files[0]

            result: FileDb = await files_repository \
                .fetch_db_file(str(expected_result.file_path))

            assert_that(result).is_equal_to(expected_result)

    @pytest.mark.asyncio
    async def test__file_does_not_exists__raises_error(
            self, files_repository: FilesRepository, db: Database
    ) -> None:
        async with db.transaction(force_rollback=True):
            with pytest.raises(FileDoesNotExistsError):
                await files_repository.fetch_db_file('fake_file_path/fake_file')


class TestCreateFile:
    test_data: List[Tuple[Dict[str, Any], FileRead]] = [
        (
            {
                'loid': 10003, 'file_path': 'test_path/test_file.json',
                'file_size': 10 * bytes_in_mb, 'user_info': user_id_3,
                'checksum': '6a1cebc7-6f83-40c3-a63b-6ae4c77fce16'
            },
            FileRead(file_path=Path('test_path/test_file.json'), file_size_mb=10,
                     checksum='6a1cebc7-6f83-40c3-a63b-6ae4c77fce16')
        ),
        (
            {
                'loid': 10003, 'file_path': 'test_path/test_file.json',
                'file_size': 10 * bytes_in_mb, 'user_info': user_id_3,
                'checksum': ''
            },
            FileRead(file_path=Path('test_path/test_file.json'), file_size_mb=10)
        )
    ]

    @pytest.mark.parametrize('data,expected_result', test_data)
    @pytest.mark.asyncio
    async def test__data_with_checksum__inserted_with_checksum(
            self, files_repository: FilesRepository, db: Database,
            data: Dict[str, Any], expected_result: FileRead
    ) -> None:
        async with db.transaction(force_rollback=True):
            result: FileRead = await files_repository.create_file(
                data['loid'], data['file_path'], data['file_size'],
                data['checksum'], data['user_info']
            )

            assert_that(result).is_equal_to(expected_result)
