FROM python:3.10

WORKDIR /opt/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV POETRY_VERSION=1.3.1
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VENV=/opt/poetry-venv

RUN ln -s /usr/bin/python3.10 /usr/bin/python

RUN python -m pip install poetry==${POETRY_VERSION}

COPY . .

RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi
ENV PYTHONPATH="$PYTHONPATH:opt/app/"


CMD ["./wait-for-it.sh", "django:8000", "--", "python", "load_data.py" ]

