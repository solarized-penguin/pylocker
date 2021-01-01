from typing import List, Union, Tuple

from fastapi import APIRouter, Depends, Header, UploadFile, File
from fastapi import Response, BackgroundTasks

from app.auth_client import logged_user
from app.core import Settings
from app.repositories.blob_repository import BlobRepository
from app.repositories.files_repository import FilesRepository
from app.routers.utils import upload_file_generator, calculate_checksums, extract_paths
from app.schemas.files import FileRead

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
        user_email: str = Depends(logged_user)
) -> Union[List[FileRead], Response]:
    files: List[FileRead] = await files_repository.fetch_all_user_files(user_email)

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
        files: List[UploadFile] = File(..., description='files to upload'),
        paths: str = Header(..., description='file_name=file_path,file_name=file_path,...'),
        blob_repository: BlobRepository = Depends(BlobRepository.create),
        files_repository: FilesRepository = Depends(FilesRepository.create),
        settings: Settings = Depends(Settings.get),
        user_email: str = Depends(logged_user)
) -> List[FileRead]:
    results: List[FileRead] = []
    mapped_files: List[Tuple[str, UploadFile]] = extract_paths(paths=paths, files=files)

    for path, file in mapped_files:
        loid: int = await blob_repository.create_blob()
        offset: int = 0
        async for chunk in upload_file_generator(file, settings):
            await blob_repository.write_to_blob(loid, offset, chunk)
            offset += len(chunk)
        file_read: FileRead = await files_repository.create_file(
            loid, path, offset, '', user_email
        )
        results.append(file_read)

    background_tasks.add_task(
        calculate_checksums,
        [path for path, file in mapped_files],
        settings, files_repository, blob_repository
    )

    return results
