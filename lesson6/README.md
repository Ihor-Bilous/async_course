# CVE parser

## How to run?

### Preparation
1. Create virtualenv and install libraries from requirements.txt file.
2. In root of lesson6 (alongside `docker-compose.yml`, `main.py` and `README.md` file) create `.env` file.

You can copy next text with default values and put it into `.env`:
```
BULK_INSERT_BATCH_SIZE=2000
EXTRACTOR_WORKERS_NUMBER=40
LOADER_WORKERS_NUMBER=10

POSTGRES_USER=testuser
POSTGRES_PASSWORD=testpass
POSTGRES_DB=testapp
```

### Run script
```shell
python main.py /home/user_name/dev/cvelistV5/cves
```

### Migrations
```shell
alembic revision --autogenerate -m "create cve table"
alembic upgrade head  # upgrade to last migration
alembic upgrade <revision_id>
alembic upgrade +1  # upgrade to next migration

alembic downgrade base  # downgrade to the beginning
alembic downgrade <revision_id>
alembic downgrade -1  # downgrade to previous migration
```

### Check results
Review and change if you are interested:
```shell
 python check_results.py
```