# flake8: noqa: E402
import os
import sys
from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session

parent_dir = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(parent_dir)

from models import Alert
from schemas.schemas import AlertCreate


def create_alert(db: Session, create_alert: AlertCreate):
    db_alert = Alert(**create_alert.model_dump())
    db.add(db_alert)
    db.commit()

    # db_alert.picture_id でpictureテーブルから、pictureを取得
    # {"picture": <picture>}の形式で返す
    # ※型はstring

    return {"picture_id": db_alert.picture_id}
