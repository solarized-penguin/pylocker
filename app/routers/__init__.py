from fastapi import FastAPI


def register_routers(app: FastAPI):
    """
    Registers all routers.
    :param app: FastAPI application instance
    """
    from .files import router as files_router

    app.include_router(files_router, prefix='/files', tags=['files'])
