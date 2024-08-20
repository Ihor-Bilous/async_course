# Lesson 7

## Preparation
Install dependencies
```shell
pip install -r requirements.txt
```

## How to run?

### WSGI application
```shell
gunicorn wsgi_app:app
```

### ASGI application
```shell
gunicorn asgi_app:app --worker-class uvicorn.workers.UvicornWorker
```
Or
```shell
uvicorn asgi_app:app
```

### Starlette application
```shell
gunicorn starlette_app:app --worker-class uvicorn.workers.UvicornWorker
```
Or
```shell
uvicorn starlette_app:app
```

### FastAPI application
```shell
gunicorn fastapi_app:app --worker-class uvicorn.workers.UvicornWorker
```
Or
```shell
uvicorn fastapi_app:app
```