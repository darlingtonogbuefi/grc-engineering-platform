# ==============================================================================
# GRC Engineering Platform
# Production Container
# ==============================================================================


FROM python:3.12-slim


LABEL maintainer="GRC Engineering Platform Team"

LABEL description="Enterprise GRC evidence automation platform"


WORKDIR /app


ENV PYTHONUNBUFFERED=1

ENV PYTHONDONTWRITEBYTECODE=1


COPY requirements.txt .


RUN pip install \
    --no-cache-dir \
    --upgrade pip \
    && pip install \
    --no-cache-dir \
    -r requirements.txt


COPY . .


RUN mkdir -p \
    evidence/raw \
    evidence/processed \
    evidence/runs \
    evidence/archive \
    reports \
    output


RUN useradd \
    --create-home \
    grcuser


RUN chown -R grcuser:grcuser /app


USER grcuser


ENTRYPOINT ["python", "-m", "engine"]
