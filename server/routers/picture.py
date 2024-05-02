# type: ignore
# flake8: noqa: E402
import os
import sys

from fastapi import APIRouter, Path
from starlette import status

parent_dir = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(parent_dir)

from cruds import picture as picture_cruds
from dependencies import Dependencies
from schemas.schemas import PictureCreate, PictureResponse

dependencies = Dependencies()
DBDependency = dependencies.get_db_dependency()

router = APIRouter(prefix="/picture", tags=["picture"])


@router.get(
    "/{picture_id}", response_model=PictureResponse, status_code=status.HTTP_200_OK
)
async def find_by_id(db: DBDependency, picture_id: int = Path(gt=0)):
    """
    Get a picture_id.

    Args:
        db (DBDependency): The database dependency object.
        picture_id (int): The ID of the picture to retrieve.

    Returns:
        PictureResponse: The response containing the picture.
    """

    return picture_cruds.find_by_id(db, picture_id)


@router.post("", response_model=PictureResponse, status_code=status.HTTP_201_CREATED)
async def create_picture(db: DBDependency, create_picture: PictureCreate):
    """
    Creates a picture in the database using the provided session and picture data.

    Args:
        db (DBDependency): The database session object.
        create_picture (PictureCreate): The picture data to create.

    Returns:
        PictureResponse: The response containing the created picture.
    """

    return picture_cruds.create_picture(db, create_picture)
