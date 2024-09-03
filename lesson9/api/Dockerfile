FROM python:3.12.5

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY cvelist /app/cvelist
COPY migrations /app/migrations
COPY app.py /app/app.py
COPY alembic.ini /app/alembic.ini


