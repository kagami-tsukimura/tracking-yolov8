# type: ignore
# flake8: noqa: E402
import os
import sys

from fastapi import APIRouter
from starlette import status

parent_dir = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(parent_dir)

from cruds import alert as alert_cruds
from dependencies import Dependencies
from schemas.schemas import AlertCreate, AlertResponse

dependencies = Dependencies()
DBDependency = dependencies.get_db_dependency()

router = APIRouter(prefix="/alert", tags=["alert"])


@router.post("", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert(db: DBDependency, create_alert: AlertCreate):
    return alert_cruds.create_alert(db, create_alert)
