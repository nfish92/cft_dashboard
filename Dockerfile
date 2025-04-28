﻿FROM python:3.13.3-slim-bookworm

# patch OS packages, install compilers, then clean up
WORKDIR /app
COPY requirements.txt ./

RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get remove -y build-essential \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

COPY . .
EXPOSE 5000
CMD ["gunicorn", "-k", "eventlet", "-w", "1", "--bind", "0.0.0.0:5000", "manage:app"]
