from fastapi import FastAPI


def register_routers(app: FastAPI) -> None:
    """
    Registers all routers.
    :param app: FastAPI application instance
    """
    from .resumable_files_router import router as resumable_files
    from .files_router import router as files
    from app.routers.users_router import router as users

    app.include_router(resumable_files, prefix='/resumable/files', tags=['/resumable/files'])
    app.include_router(files, prefix='/files', tags=['/files'])
    app.include_router(users, prefix='/users', tags=['/users'])
