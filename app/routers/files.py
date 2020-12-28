from fastapi import APIRouter
from fastapi.responses import JSONResponse

from ..schemas.files import FileRead

router = APIRouter()


@router.post(
    ''
)
async def create_upload() -> JSONResponse:
    pass


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
