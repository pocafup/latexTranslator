# syntax=docker/dockerfile:1.6
FROM python:3.11-slim AS base

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    texlive-xetex \
    texlive-latex-base texlive-latex-recommended texlive-latex-extra \
    texlive-fonts-recommended lmodern latexmk \
    fonts-dejavu fonts-freefont-ttf ca-certificates curl \
    font-noto-serif-cjk-sc font-noto-serif-cjk-jp font-noto-serif-cjk-kr \ 
    font-noto-sans-cjk-sc   font-noto-sans-cjk-jp   font-noto-sans-cjk-kr

 && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip && pip install "poetry==2.1.2"

COPY pyproject.toml poetry.lock* ./

RUN poetry install --no-interaction --no-ansi --no-root

COPY . .

EXPOSE 8501

CMD ["poetry","run","streamlit","run","ui.py","--server.address=0.0.0.0","--server.headless","true","--browser.gatherUsageStats","false"]