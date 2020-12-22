from fastapi import FastAPI


def register_routers(app: FastAPI) -> None:
    """
    Registers all routers.
    :param app: FastAPI application instance
    """
    from .files import router as files_router
    from ..security.users_router import router as user_router

    app.include_router(files_router, prefix='/files', tags=['files'])
    app.include_router(user_router, prefix='/users', tags=['users'], include_in_schema=False)
