FROM python:3.10

WORKDIR /opt/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV POETRY_VERSION=1.3.2
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VENV=/opt/poetry-venv

RUN ln -s /usr/bin/python3.10 /usr/bin/python

RUN python -m pip install poetry==${POETRY_VERSION}
RUN pip install gunicorn

COPY src ./src
COPY tests ./tests
COPY poetry.lock .
COPY pyproject.toml .

RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi
ENV PYTHONPATH="$PYTHONPATH:/opt/app/src:/opt/app/tests"

CMD [ "gunicorn", "src.main:app",\
"--chdir", "/opt/app/src",\
"--workers", "4",\
"--worker-class", "uvicorn.workers.UvicornWorker",\
"--bind", "0.0.0.0:8200"]

