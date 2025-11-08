# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY scripts ./scripts
COPY dataset ./dataset

ENTRYPOINT ["python", "scripts/generate_messy_datasets.py"]
CMD ["--input-dir", "/app/dataset", "--output-dir", "/app/output", "--seed", "42"]
