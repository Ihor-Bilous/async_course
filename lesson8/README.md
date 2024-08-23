# Lesson 8

## Preparation
In root of lesson8 (alongside `docker-compose.yml`, and `README.md` file) create `.env` file.
You can copy next text with default values and put it into `.env`:
```
POSTGRES_USER=testuser
POSTGRES_PASSWORD=testpass
POSTGRES_DB=testapp
```

Or you can run next command
```shell
echo "POSTGRES_USER=testuser
POSTGRES_PASSWORD=testpass
POSTGRES_DB=testapp" > .env
```

Install dependencies:
```shell
pip install -r requirements.txt
```

Run DB:
```shell
docker-compose up
```

Migrate DB:
```shell
alembic upgrade head
```

## How to run API?

### Via Gunicorn
```shell
gunicorn cvelist.app:app --worker-class uvicorn.workers.UvicornWorker
```

### Via Uvicorn
```shell
uvicorn cvelist.app:app
```

## Try API

Open in browser http://localhost:8000/docs and start using API.
