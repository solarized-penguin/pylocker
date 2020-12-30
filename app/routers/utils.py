from hashlib import md5
from typing import AsyncGenerator, Union, List

from fastapi import UploadFile

from app.core import Settings
from app.repositories.blob_repository import BlobRepository
from app.repositories.files_repository import FilesRepository
from app.schemas.files import FileDb


async def calculate_hash(
        loid: int, blob_repository: BlobRepository, settings: Settings
) -> str:
    md5_hash = md5()
    block_size: int = settings.max_chunk_size
    offset: int = 0

    chunk: bytes = await blob_repository.read_from_blob(loid, offset, block_size)

    while chunk:
        md5_hash.update(chunk)
        offset += len(chunk)
        chunk = await blob_repository.read_from_blob(loid, offset, block_size)

    return md5_hash.hexdigest()


async def upload_file_generator(file: UploadFile, settings: Settings) -> AsyncGenerator[bytes, None]:
    while True:
        chunk: Union[bytes, str] = await file.read(settings.max_chunk_size)

        chunk = chunk if isinstance(chunk, bytes) else chunk.encode('utf-8')

        if not chunk:
            break

        yield chunk


async def calculate_checksum(
        file_path: str, settings: Settings,
        files_repository: FilesRepository, blob_repository: BlobRepository
) -> None:
    file_db: FileDb = await files_repository.fetch_db_file(file_path)

    if not file_db.file_checksum:
        checksum = await calculate_hash(file_db.oid, blob_repository, settings)

        await files_repository.update_file_data(
            str(file_db.file_path), file_checksum=checksum
        )


async def calculate_checksums(
        file_paths: List[str], settings: Settings,
        files_repository: FilesRepository, blob_repository: BlobRepository
) -> None:
    for file_path in file_paths:
        file_db: FileDb = await files_repository.fetch_db_file(file_path)

        if not file_db.file_checksum:
            checksum = await calculate_hash(file_db.oid, blob_repository, settings)

            await files_repository.update_file_data(
                str(file_db.file_path), file_checksum=checksum
            )
