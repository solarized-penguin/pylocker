from fastapi import APIRouter, Depends

from ..security import security_scheme

router = APIRouter()


@router.get('/')
async def all_files(token: str = Depends(security_scheme)):
    return {'token': token}
