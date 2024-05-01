# type: ignore
# flake8: noqa: E402
import os
import sys

from fastapi import APIRouter
from starlette import status

parent_dir = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(parent_dir)

from cruds import picture as picture_cruds
from dependencies import Dependencies
from schemas.schemas import PictureCreate, PictureResponse

dependencies = Dependencies()
DBDependency = dependencies.get_db_dependency()

router = APIRouter(prefix="/picture", tags=["picture"])


@router.post("", response_model=PictureResponse, status_code=status.HTTP_201_CREATED)
async def create_picture(db: DBDependency, create_picture: PictureCreate):
    return picture_cruds.create_picture(db, create_picture)
