from fastapi import APIRouter, Depends
from starlette.requests import Request

from ..blob_manager import BlobManager
from ..schemas.files import FileRead
from ..security import logged_user, UserInfo

router = APIRouter()


@router.post(
    '/',
    response_model=FileRead,
    status_code=200
)
async def upload_file(
        request: Request,
        blob_manager: BlobManager = Depends(BlobManager.create_manager),
        user_info: UserInfo = Depends(logged_user)
) -> FileRead:
    loid: int = await blob_manager.create_blob()

    offset: int = 0
    async for chunk in request.stream():
        await blob_manager.write_to_blob(
            loid=loid, offset=offset, data=chunk
        )
        offset += len(chunk)
