FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8
WORKDIR /app

RUN echo 'upgrading pip...'
RUN python -m pip install --upgrade pip

RUN echo 'downloading poetry'
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py\
    | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

COPY ./pyproject.toml ./poetry.lock* ./

RUN echo 'installing packages:'
RUN poetry install --no-root --no-dev

RUN echo 'coping needed files...'
COPY ./app ./app/
COPY ./migrations ./migrations/
COPY ./alembic.ini ./
COPY ./docker/main.py ./main.py
COPY ./docker/prestart.sh ./prestart.sh

RUN echo 'exposing port 80'
EXPOSE 80

RUN echo 'building image has concluded'
