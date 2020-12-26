from fastapi import APIRouter, Depends
from starlette.requests import Request

from ..daos.blob_dao import BlobDao
from ..daos.files_dao import FilesDao
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
        blob_dao: BlobDao = Depends(BlobDao.create_dao),
        files_dao: FilesDao = Depends(FilesDao.create_dao),
        user_info: UserInfo = Depends(logged_user)
) -> FileRead:
    loid: int = await blob_dao.create_blob()

    offset: int = 0
    async for chunk in request.stream():
        await blob_dao.write_to_blob(
            loid=loid, offset=offset, data=chunk
        )
        offset += len(chunk)

    return await files_dao.create_file(
        loid, 'todo', 1, user_info
    )
