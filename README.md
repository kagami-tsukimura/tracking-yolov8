# Object Detection with YOLOv8

This project focuses on the object detection task using the [YOLOv8](https://github.com/ultralytics/ultralytics) model.

## How to Use

1. Clone this repository to your local machine.
2. Please install [CUDA](https://developer.nvidia.com/cuda-downloads).
3. Set up a virtual environment and install the required dependencies using the provided `server/environ/requirements.txt`.

   ```bash
   python3 -m venv yolo
   pip install -r server/environ/requirements.txt
   ```

4. Please execute with the following code.

   ```bash: Detection for Camera
   python3 object_detection_yolov8.py
   ```

   ```bash: Detection for Video
   python3 object_detection_yolov8.py --video <mp4 file path>
   ```

## Docker

Please see [Docker](./server/docker-compose.yml)

### How To Up Docker

```bash
docker-compose up -d
```

### How To Down Docker

```bash
docker-compose down
```

### Setup Database

1. Execute FastAPI Container

```bash
docker-compose exec <FasAPI CONTAINER ID> bash
```

2. Create Database Migrations Environment

- On FastAPI Container

```bash
alembic init migrations
```

3. Grant User Permissions

- On Local

```bash
sudo chown -R $(whoami):$(whoami) migrations/ alembic.ini
```

4. Fix `alembic.ini`

- On Local

```ini
sqlalchemy.url = postgresql://postgres:postgres@postgres:5432/admin
```

5. Fix `migrations/env.py`

- On Local

```python
from models import Base

target_metadata = Base.metadata
```

6. Run Migrations

- On FastAPI Container

```bash
alembic revision --autogenerate -m "Create table"
```

7. Apply Migrations

- On FastAPI Container

```bash
alembic upgrade head
```

### Connect PgAdmin

Please see [Docker](./server/docker-compose.yml)

- General
  - Name: postgres
- Connect
  - Host/Address: postgres
  - Port: 5432
  - User: postgres
  - Password: postgres

## Table Layout

![overview](plantuml/erd.svg)
