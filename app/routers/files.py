from fastapi import APIRouter, Depends
from starlette.requests import Request

from ..schemas.files import FileRead
from ..security import security_scheme

router = APIRouter()


@router.post(
    '/',
    response_model=FileRead,
    status_code=200
)
async def upload_files(
        request: Request,
        token: str = Depends(security_scheme)
) -> FileRead:
    async for chunk in request.stream():
        pass
