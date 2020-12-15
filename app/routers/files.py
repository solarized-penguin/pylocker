from fastapi import APIRouter

router = APIRouter()


@router.get('/')
async def all_files():
    return {'message': 'result'}
