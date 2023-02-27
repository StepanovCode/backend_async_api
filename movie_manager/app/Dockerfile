FROM python:3.10

WORKDIR /opt/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV UWSGI_PROCESSES 1
ENV UWSGI_THREADS 16
ENV UWSGI_HARAKIRI 240
ENV DJANGO_SETTINGS_MODULE 'config.settings'

ENV POETRY_VERSION=1.3.1
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VENV=/opt/poetry-venv

RUN ln -s /usr/bin/python3.10 /usr/bin/python

RUN python -m pip install poetry==${POETRY_VERSION}
RUN python -m pip install uwsgi

RUN mkdir -p /opt/app/staticfiles/ \
    && mkdir -p /opt/app/mediafiles/

COPY . .

RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi
ENV PYTHONPATH="$PYTHONPATH:opt/app/"

RUN chmod +x wait-for-it.sh
RUN chmod +x entrypoint.sh

CMD ["./wait-for-it.sh", "postgres:5432", "--", "./entrypoint.sh" ]
