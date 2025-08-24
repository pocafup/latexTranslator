# syntax=docker/dockerfile:1.6
FROM python:3.11-slim AS base

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo zlib1g curl \
 && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip && pip install "poetry==${POETRY_VERSION}"

COPY pyproject.toml poetry.lock* ./
RUN poetry install

COPY . .

EXPOSE 8501

CMD ["poetry","run","streamlit","run","ui.py","--server.address=0.0.0.0","--server.headless","true","--browser.gatherUsageStats","false"]
