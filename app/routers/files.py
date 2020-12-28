from secrets import token_urlsafe
from typing import Dict, Any

from aredis import StrictRedis
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import JSONResponse

from ..core import get_redis, Settings
from ..errors import LocationNotFoundError, ChunkTooBigError
from ..repositories.blob_repository import BlobRepository
from ..repositories.files_repository import FilesRepository
from ..schemas.files import UploadCreationHeaders, UploadCacheData, UploadLocationData, UploadFileHeaders
from ..security import UserInfo, logged_user

router = APIRouter()


@router.post(
    '',
    response_model=UploadLocationData,
    status_code=201
)
async def create_upload(
        headers: UploadCreationHeaders = Depends(UploadCreationHeaders.as_header),
        redis: StrictRedis = Depends(get_redis),
        user_info: UserInfo = Depends(logged_user),
        blob_repository: BlobRepository = Depends(BlobRepository.create),
        settings: Settings = Depends(Settings.get)
) -> UploadLocationData:
    loid: int = await blob_repository.create_blob()
    location: str = token_urlsafe(settings.location_url_bytes)

    upload_cache_data = UploadCacheData(
        owner_id=user_info.id,
        loid=loid,
        upload_length=headers.upload_length,
        file_path=str(headers.file_path)
    )

    await redis.set(location, upload_cache_data.json())

    return UploadLocationData(location=location)


@router.patch(
    '',
    status_code=200
)
async def upload_file(
        chunk: bytes,
        location: str = Query(..., description='upload location'),
        headers: UploadFileHeaders = Depends(UploadFileHeaders.as_header),
        redis: StrictRedis = Depends(get_redis),
        blob_repository: BlobRepository = Depends(BlobRepository.create),
        files_repository: FilesRepository = Depends(FilesRepository.create),
        settings: Settings = Depends(Settings.get),
        user_info: UserInfo = Depends(logged_user)
) -> JSONResponse:
    redis_data: Dict[str, Any] = await redis.get(location)

    if not redis_data: raise LocationNotFoundError()
    if len(chunk) > settings.max_chunk_size: raise ChunkTooBigError()

    cache_data: UploadCacheData = UploadCacheData(**redis_data)

    if user_info.id != cache_data.owner_id:
        raise HTTPException(status_code=403, detail='No privilege to access file!')

    await blob_repository.write_to_blob(
        cache_data.loid, headers.upload_offset, chunk
    )

    if (headers.upload_offset + len(chunk)) >= cache_data.upload_length:
        await files_repository.create_file(
            cache_data.loid, cache_data.file_path, cache_data.upload_length, user_info
        )
        await redis.delete(location)
        return JSONResponse(status_code=204)

    return JSONResponse(status_code=200)


@router.head(
    ''
)
async def fetch_upload_offset() -> JSONResponse:
    pass


@router.delete(
    ''
)
async def delete_file() -> JSONResponse:
    pass
