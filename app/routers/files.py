from fastapi import APIRouter, Depends
from starlette.requests import Request

from ..repositories.blob_repository import BlobRepository
from ..repositories.files_repository import FilesRepository
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
        blob_repository: BlobRepository = Depends(BlobRepository.create),
        files_repository: FilesRepository = Depends(FilesRepository.create),
        user_info: UserInfo = Depends(logged_user)
) -> FileRead:
    loid: int = await blob_repository.create_blob()

    offset: int = 0
    async for chunk in request.stream():
        await blob_repository.write_to_blob(
            loid=loid, offset=offset, data=chunk
        )
        offset += len(chunk)

    return await files_repository.create_file(
        loid, 'todo', 1, user_info
    )
