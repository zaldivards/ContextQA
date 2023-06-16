FROM python:3.11-slim

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /app

COPY ./Pipfile* /app/

RUN python -m pip install --upgrade pip && \
    python -m pip install pipenv && \
    pipenv install --clear --system



