from secrets import token_urlsafe

from aredis import StrictRedis
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from ..core import get_redis
from ..repositories.blob_repository import BlobRepository
from ..schemas.files import FileRead, UploadCreationHeaders, UploadCacheData, UploadLocationData
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
        blob_repository: BlobRepository = Depends(BlobRepository.create)
) -> UploadLocationData:
    loid: int = await blob_repository.create_blob()
    location: str = token_urlsafe()

    upload_location = UploadCacheData(
        owner_id=user_info.id,
        loid=loid,
        file_path=str(headers.file_path)
    )

    await redis.set(location, upload_location.json())

    return UploadLocationData(location=location)


@router.patch(
    '',
    response_model=FileRead,
    status_code=200
)
async def upload_file() -> FileRead:
    pass


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
