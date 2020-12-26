from typing import List, Tuple

import pytest
from assertpy import assert_that
from databases import Database

from app.daos.blob_dao import BlobDao


@pytest.fixture(scope='function')
def blob_dao(db: Database) -> BlobDao:
    return BlobDao.create_dao(db)


class TestCreateBlob:
    lowest_possible_blob_oid: int = 10000

    @pytest.mark.asyncio
    async def test__works_correctly__oid_created(
            self, blob_dao: BlobDao, db: Database
    ) -> None:
        async with db.transaction(force_rollback=True):
            loid: int = await blob_dao.create_blob()

            assert_that(loid).is_greater_than_or_equal_to(
                self.lowest_possible_blob_oid
            )


test_blob_content = 'This is test blob content'


async def write_to_blob(blob_dao: BlobDao, data: bytes) -> int:
    """
    Creates blob and writes data to it.
    :param blob_dao: BlobDao instance
    :param data: blobs content
    :return: Blobs oid
    :rtype: int
    """
    loid: int = await blob_dao.create_blob()

    await blob_dao.write_to_blob(
        loid=loid, offset=0, data=data
    )
    return loid


class TestWriteToBlob:

    @pytest.mark.asyncio
    async def test__data_supplied_correctly__data_written_to_blob(
            self, blob_dao: BlobDao, db: Database
    ) -> None:
        async with db.transaction(force_rollback=True):
            blob_content: bytes = test_blob_content.encode('utf-8')
            loid: int = await write_to_blob(blob_dao, blob_content)

            result: bytes = await db.execute('SELECT lo_get(:loid)', {'loid': loid})

            assert_that(result).is_equal_to(blob_content)


class TestReadFromBlob:
    blob_content: bytes = test_blob_content.encode('utf-8')

    test_data: List[Tuple[int, bytes]] = [
        (len(blob_content), blob_content),
        (10, blob_content[:10]),
        (3, blob_content[:3])
    ]

    @pytest.mark.parametrize('length,expected_result', test_data)
    @pytest.mark.asyncio
    async def test__length_defined_correctly__returns_correct_part_of_content(
            self, blob_dao: BlobDao, db: Database,
            length: int, expected_result: bytes
    ) -> None:
        async with db.transaction(force_rollback=True):
            loid: int = await write_to_blob(blob_dao, self.blob_content)

            result: bytes = await blob_dao.read_from_blob(
                loid=loid, offset=0, length=length
            )

            assert_that(result).is_equal_to(expected_result)


class TestRemoveBlob:

    @pytest.mark.asyncio
    async def test__blob_with_selected_oid_exists__returns_true(
            self, blob_dao: BlobDao, db: Database
    ) -> None:
        async with db.transaction(force_rollback=True):
            blob_content: bytes = test_blob_content.encode('utf-8')
            loid: int = await write_to_blob(blob_dao, blob_content)

            result: bool = await blob_dao.remove_blob(loid=loid)

            assert_that(result).is_true()


class TestGetLastByte:
    data_one = test_blob_content.encode('utf-8')
    data_two = test_blob_content[:15].encode('utf-8')
    data_three = test_blob_content[:10].encode('utf-8')

    test_data: List[Tuple[bytes, int]] = [
        (data_one, len(data_one)),
        (data_two, len(data_two)),
        (data_three, len(data_three))
    ]

    @pytest.mark.parametrize('blob_data,expected_result', test_data)
    @pytest.mark.asyncio
    async def test__blob_with_supplied_oid_exists__returns_last_byte(
            self, blob_dao: BlobDao, db: Database,
            blob_data: bytes, expected_result: int
    ) -> None:
        async with db.transaction(force_rollback=True):
            loid: int = await write_to_blob(blob_dao, blob_data)

            result: int = await blob_dao.get_last_byte(loid=loid)

            assert_that(result).is_equal_to(expected_result)
