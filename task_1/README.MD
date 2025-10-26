## Run PostgreSQL in a Docker container:

```bash
docker run -d \
  --name postgres_local \
  -p 5432:5432 \
  -e POSTGRES_DB=postgres_db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -v postgres_data:/var/lib/postgresql/data \
  --restart unless-stopped \
  postgres:latest
```

## Development Setup

### Install dependencies with Poetry:

```bash
poetry install
```

### Run scripts with Poetry:

```bash
poetry run python setup.py    # Setup database
poetry run python seed.py     # Seed data
```