from fastapi import APIRouter, Depends
from starlette.requests import Request

from ..schemas.files import FileRead
from ..security import logged_user_id

router = APIRouter()


@router.post(
    '/',
    response_model=FileRead,
    status_code=200
)
async def upload_files(
        request: Request,
        user_id: str = Depends(logged_user_id)
) -> FileRead:
    async for chunk in request.stream():
        pass
