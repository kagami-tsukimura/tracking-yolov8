# flake8: noqa: E402
import os
import sys

from sqlalchemy.orm import Session

parent_dir = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(parent_dir)

from cruds import picture as picture_cruds
from models import Alert
from schemas.schemas import AlertCreate


def create_alert(db: Session, create_alert: AlertCreate):
    """
    Creates an alert in the database using the provided session and alert data.

    Args:
        db (Session): The database session object.
        create_alert (AlertCreate): The alert data to create.

    Returns:
        PictureResponse: The response containing the picture.
    """

    db_alert = Alert(**create_alert.model_dump())
    db.add(db_alert)
    db.commit()

    res_picture_id = db_alert.picture_id

    return picture_cruds.find_by_id(db, res_picture_id)
