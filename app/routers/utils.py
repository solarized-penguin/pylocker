from hashlib import md5

from app.core import Settings
from app.repositories.blob_repository import BlobRepository


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

        print(offset)

    return md5_hash.hexdigest()
