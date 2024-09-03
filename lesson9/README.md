# CVE api & loader

## How to run?

### API
1. cd api
2. create .env. You can copy next variables into file:
```
POSTGRES_USER=testuser
POSTGRES_PASSWORD=testpass
POSTGRES_DB=testapp
DB_HOST=cve_postgres
```
You can see default values in `api/cvelist/config`
3. Build and run `docker-compose build && docker-compose up`
4. Run migrations `docker-compose run api alembic upgrade head`


1. cd data_loader
2. create .env. You can copy next variables into file:
```
FETCHING_EXTRACTOR_WORKERS_NUMBER=5
FETCHING_LOADER_WORKERS_NUMBER=2
```
You can see default values in `data_loader/cvelist/config`
3. create virtualenv `python -m venv venv`
4. activate venv `source venv/bin/activate`
5. Install requirements`pip install -r requirements.txt`
6. Run loader `python load_cve.py`