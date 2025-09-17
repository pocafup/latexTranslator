# syntax=docker/dockerfile:1.6
FROM python:3.11-slim AS base

WORKDIR /latextranslator

RUN apt-get update && apt-get install -y --no-install-recommends \
    texlive-xetex \
    texlive-latex-base \
    texlive-latex-recommended \
    texlive-latex-extra \
    texlive-lang-spanish \
    texlive-fonts-recommended \
    lmodern \
    latexmk \
    fonts-dejavu \
    fonts-freefont-ttf \
    fonts-liberation \
    fonts-liberation2 \
    fonts-noto-cjk \
    texlive-pictures \
    texlive-lang-chinese \
    ca-certificates \
    curl \
 && rm -rf /var/lib/apt/lists/*
# RUN tlmgr install pgf

RUN pip install --upgrade pip && pip install "poetry==2.1.2"  

COPY pyproject.toml poetry.lock* ./

RUN poetry install --no-interaction --no-ansi --no-root

RUN poetry run pip install openai

COPY . .

EXPOSE 8501

CMD ["poetry","run","streamlit","run","ui.py","--server.address=0.0.0.0","--server.headless","true","--browser.gatherUsageStats","false"]