from secrets import token_urlsafe
from typing import Optional, List, Union

from aredis import StrictRedis
from fastapi import APIRouter, Depends, Query, HTTPException, File
from fastapi.responses import JSONResponse, Response

from .utils import calculate_hash
from ..core import get_redis, Settings
from ..errors import LocationNotFoundError, ChunkTooBigError
from ..repositories.blob_repository import BlobRepository
from ..repositories.files_repository import FilesRepository
from ..schemas.files import UploadCreationHeaders, UploadCacheData, UploadFileHeaders, FileRead, FileDb
from ..security import UserInfo, logged_user

router = APIRouter()


@router.get(
    '/all',
    response_model=List[FileRead],
    status_code=200,
    responses={
        200: {'description': 'All files that belong to user returned successfully.'},
        204: {'description': 'User has no files.'}
    }
)
async def fetch_user_files(
        files_repository: FilesRepository = Depends(FilesRepository.create),
        user_info: UserInfo = Depends(logged_user)
) -> Union[List[FileRead], Response]:
    files: List[FileRead] = await files_repository.fetch_all_user_files(user_info)

    if not files:
        return Response(status_code=204)

    return files


@router.get(
    '',
    status_code=200
)
async def download_file(
        file_path: str = Query(..., description='File path of the file to download.'),
        upload_offset: int = Query(..., description='File offset to get appropriate chunk.'),
        files_repository: FilesRepository = Depends(FilesRepository.create),
        blob_repository: BlobRepository = Depends(BlobRepository.create),
        settings: Settings = Depends(Settings.get),
        user_info: UserInfo = Depends(logged_user)
) -> bytes:
    file_db: FileDb = await files_repository.fetch_db_file(file_path)

    if file_db.owner_id != user_info.id:
        raise HTTPException(status_code=403, detail='No privileges to access file.')

    chunk: bytes = await blob_repository.read_from_blob(
        file_db.oid, upload_offset, settings.max_chunk_size
    )

    return chunk


@router.post(
    '',
    status_code=201
)
async def create_new_upload(
        headers: UploadCreationHeaders = Depends(UploadCreationHeaders.as_header),
        redis: StrictRedis = Depends(get_redis),
        user_info: UserInfo = Depends(logged_user),
        blob_repository: BlobRepository = Depends(BlobRepository.create),
        settings: Settings = Depends(Settings.get)
) -> JSONResponse:
    loid: int = await blob_repository.create_blob()
    location: str = token_urlsafe(settings.location_url_bytes)

    upload_cache_data = UploadCacheData(
        owner_id=user_info.id,
        loid=loid,
        file_path=str(headers.file_path)
    )

    await redis.set(location, upload_cache_data.json())

    return JSONResponse(
        status_code=201,
        headers={'location': location}
    )


@router.patch(
    '',
    status_code=200
)
async def upload_file(
        chunk: bytes = File(..., description='chunk of the file'),
        location: str = Query(..., description='upload location'),
        headers: UploadFileHeaders = Depends(UploadFileHeaders.as_header),
        redis: StrictRedis = Depends(get_redis),
        blob_repository: BlobRepository = Depends(BlobRepository.create),
        settings: Settings = Depends(Settings.get),
        user_info: UserInfo = Depends(logged_user)
) -> JSONResponse:
    if not await redis.exists(location):
        raise LocationNotFoundError()
    if len(chunk) > settings.max_chunk_size:
        raise ChunkTooBigError()

    redis_data: bytes = await redis.get(location)
    cache_data: UploadCacheData = UploadCacheData.parse_raw(redis_data)

    if user_info.id != cache_data.owner_id:
        raise HTTPException(status_code=403, detail='No privileges to access file.')

    await blob_repository.write_to_blob(
        cache_data.loid, headers.upload_offset, chunk
    )

    return JSONResponse(status_code=200)


@router.post(
    '/confirm',
    response_model=FileRead,
    status_code=201
)
async def confirm_upload(
        location: str = Query(..., description='upload location'),
        checksum: Optional[str] = Query(None, description='checksum of the file - for optional validation'),
        redis: StrictRedis = Depends(get_redis),
        blob_repository: BlobRepository = Depends(BlobRepository.create),
        files_repository: FilesRepository = Depends(FilesRepository.create),
        settings: Settings = Depends(Settings.get),
        user_info: UserInfo = Depends(logged_user)
) -> FileRead:
    if not await redis.exists(location):
        raise LocationNotFoundError()

    redis_data: bytes = await redis.get(location)
    cache_data: UploadCacheData = UploadCacheData.parse_raw(redis_data)

    if user_info.id != cache_data.owner_id:
        raise HTTPException(status_code=403, detail='No privileges to access file.')

    blob_checksum: str = ''
    if checksum:
        blob_checksum = await calculate_hash(cache_data.loid, blob_repository, settings)
        if checksum != blob_checksum:
            await redis.delete(location)
            raise HTTPException(status_code=460, detail="Checksums don't match. File deleted.")

    file_size: int = await blob_repository.get_last_byte(cache_data.loid)

    file_read: FileRead = await files_repository.create_file(
        cache_data.loid, cache_data.file_path, file_size,
        blob_checksum if checksum else None, user_info
    )

    await redis.delete(location)

    return file_read


@router.head(
    '',
    response_model=int,
    status_code=200
)
async def fetch_upload_offset(
        location: str = Query(..., description='upload location'),
        redis: StrictRedis = Depends(get_redis),
        blob_repository: BlobRepository = Depends(BlobRepository.create),
        user_info: UserInfo = Depends(logged_user)
) -> JSONResponse:
    if not await redis.exists(location):
        raise LocationNotFoundError()

    redis_data: bytes = await redis.get(location)
    cache_data: UploadCacheData = UploadCacheData.parse_raw(redis_data)

    if user_info.id != cache_data.owner_id:
        raise HTTPException(status_code=403, detail='No privileges to access file.')

    last_byte: int = await blob_repository.get_last_byte(cache_data.loid)

    return JSONResponse(
        status_code=200,
        headers={'upload-offset': str(last_byte)}
    )


@router.delete(
    '',
    status_code=200
)
async def delete_file(
        file_path: str = Query(..., description='path of file to delete'),
        files_repository: FilesRepository = Depends(FilesRepository.create),
        user_info: UserInfo = Depends(logged_user)
) -> JSONResponse:
    db_file: FileDb = await files_repository.fetch_db_file(file_path)

    if db_file.owner_id != user_info.id:
        raise HTTPException(status_code=403, detail='No privileges to access file.')

    await files_repository.delete_file(db_file.oid)

    return JSONResponse(
        status_code=200,
        content={
            'message': f"Operation successful. "
                       f"Object with path '{db_file.file_path}' was deleted."
        }
    )
