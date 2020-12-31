from typing import List, Union, Tuple

from fastapi import APIRouter, Depends, Header, UploadFile
from fastapi import Response, BackgroundTasks

from app.auth_client import logged_user
from app.core import Settings
from app.repositories.blob_repository import BlobRepository
from app.repositories.files_repository import FilesRepository
from app.routers.utils import upload_file_generator, calculate_checksums, extract_paths
from app.schemas.files import FileRead, FilesToUpload
from app.schemas.users import UserInfo

router: APIRouter = APIRouter()


@router.get(
    '/all',
    response_model=List[FileRead],
    status_code=200,
    responses={
        200: {'description': 'All files that belong to user returned successfully.'},
        204: {'description': 'User has no files.'}
    }
)
async def fetch_user_files(
        files_repository: FilesRepository = Depends(FilesRepository.create),
        user_info: UserInfo = Depends(logged_user)
) -> Union[List[FileRead], Response]:
    files: List[FileRead] = await files_repository.fetch_all_user_files(user_info)

    if not files:
        return Response(status_code=204)

    return files


@router.post(
    '',
    response_model=List[FileRead],
    status_code=201
)
async def upload_file(
        background_tasks: BackgroundTasks,
        upload_files: FilesToUpload = Depends(FilesToUpload.as_files),
        paths: str = Header(..., description='Paths in format file_name=file_path'),
        blob_repository: BlobRepository = Depends(BlobRepository.create),
        files_repository: FilesRepository = Depends(FilesRepository.create),
        settings: Settings = Depends(Settings.get),
        user_info: UserInfo = Depends(logged_user)
) -> List[FileRead]:
    results: List[FileRead] = []
    mapped_files: List[Tuple[str, UploadFile]] = extract_paths(paths=paths, files=upload_files.files)

    for path, file in mapped_files:
        loid: int = await blob_repository.create_blob()
        offset: int = 0
        async for chunk in upload_file_generator(file, settings):
            await blob_repository.write_to_blob(loid, offset, chunk)
            offset += len(chunk)
        file_read: FileRead = await files_repository.create_file(
            loid, path, offset, '', user_info
        )
        results.append(file_read)

    background_tasks.add_task(
        calculate_checksums,
        [path for path, file in mapped_files],
        settings, files_repository, blob_repository
    )

    return results
