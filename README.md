# Object Detection with YOLOv8

## Overview

This project focuses on the object detection task using the [YOLOv8](https://github.com/ultralytics/ultralytics) model.  
The alert of a person who has stayed continuously for a constant frame is issued by object detection.

## How to Use

### Setup Virtual Environment

<details><summary>[How To Setup Virtual Environment]</summary>

1. Clone this repository to your local machine.
2. Please install [CUDA](https://developer.nvidia.com/cuda-downloads).
3. Set up a virtual environment and install the required dependencies using the provided `server/environ/requirements.txt`.

   ```bash
   python3 -m venv yolo
   pip install -r server/environ/requirements.txt
   ```

</details>

### Setup Docker

<details><summary>[How To Setup Docker]</summary>

Please see [Docker](./server/docker-compose.yml)

Launch the following containers with Docker.

- FastAPI
- PostgreSQL
- PgAdmin
- Nginx

#### How To Up Docker

```bash
docker-compose up -d
```

#### Memo: How To Coreate Private Key

1. Run `openssl`

```bash:
openssl rand -hex 32
```

2. Set `.env`

```bash
SECRET_KEY = "YOUR_SECRET_KEY"
DATABASE_URL = "POSTGRES_DATABASE_URL"
```

#### Setup Database

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

#### Connect PgAdmin

Please see [Docker](./server/docker-compose.yml)

- General
  - Name: postgres
- Connect
  - Host/Address: postgres
  - Port: 5432
  - User: postgres
  - Password: postgres

#### How To Down Docker

```bash
docker-compose down
```

</details>

### Run the Object Detection

<details><summary>[How To Run the Object Detection]</summary>

Please execute with the following code.

- Detection for Camera

```bash
python3 object_detection_yolov8.py
```

- Detection for Video

```bash
python3 object_detection_yolov8.py --video <mp4 file path>
```

</details>

### Download Alert Files

<details><summary>[How To Download Alert Files]</summary>

The alert images are saved in nginx and can be downloaded.

```bash
cd alerts
./downloads.sh <alert_file_path>
# sample command
./downloads.sh http://localhost:8001/images/20240502_11h35m37s_person_keikoku.png
```

</details>

## Table Layout

![overview](plantuml/erd.svg)
