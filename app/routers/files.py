from secrets import token_urlsafe

from aredis import StrictRedis
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from ..core import get_redis
from ..repositories.blob_repository import BlobRepository
from ..schemas.files import FileRead, UploadCreationHeaders, UploadCreation
from ..security import UserInfo, logged_user

router = APIRouter()


@router.post(
    '',
    status_code=201
)
async def create_upload(
        headers: UploadCreationHeaders = Depends(UploadCreationHeaders.as_header),
        redis: StrictRedis = Depends(get_redis),
        user_info: UserInfo = Depends(logged_user),
        blob_repository: BlobRepository = Depends(BlobRepository.create)
) -> JSONResponse:
    loid: int = await blob_repository.create_blob()
    location: str = token_urlsafe()

    upload_location = UploadCreation(
        owner_id=user_info.id,
        loid=loid,
        file_path=str(headers.file_path)
    )

    await redis.set(location, upload_location.json())

    return JSONResponse(
        headers={
            'Location': location
        },
        status_code=201
    )


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
