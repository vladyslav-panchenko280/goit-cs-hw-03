## Run MongoDB in a Docker container:

```bash
docker run -d \
  --name mongodb_local \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=admin_password \
  -v mongodb_data:/data/db \
  --restart unless-stopped \
  mongo:latest
```

## Development Setup

### Install dependencies with Poetry:

```bash
poetry install
```

### Run scripts with Poetry:

```bash
poetry run python main.py
```
