import uvicorn

from app import create_app

app = create_app()

if __name__ == '__main__':
    uvicorn.run(
        'main_local:app',
        port=9002,
        host='0.0.0.0',
        debug=True,
        reload=True
    )
