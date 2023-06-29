FROM python:3.11-slim

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /app

COPY ./ /app/

RUN python -m pip install --upgrade pip && \
    python -m pip install pipenv && \
    pipenv install --clear --system

EXPOSE 8080

ENTRYPOINT uvicorn main:app --host 0.0.0.0 --port 8080 --reload


