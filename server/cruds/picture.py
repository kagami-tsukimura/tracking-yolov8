# flake8: noqa: E402
import os
import sys

from sqlalchemy.orm import Session

parent_dir = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(parent_dir)

from models import Picture
from schemas.schemas import PictureCreate


def find_by_id(db: Session, picture_id: int):
    return db.query(Picture).filter(Picture.picture_id == picture_id).first()


def create_picture(db: Session, create_picture: PictureCreate):
    db_picture = Picture(**create_picture.model_dump())
    db.add(db_picture)
    db.commit()

    return db_picture
