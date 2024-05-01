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
    db_alert = Alert(**create_alert.model_dump())
    db.add(db_alert)
    db.commit()

    # create_alertの前に、create_pictureの必要がある
    # picture作成して、picture_idを返す
    # picture_idをcreate_alertの引数に渡す
    # camera撮影か、mp4読み込みのどちらかのステータスをcreate_alertの引数に渡す

    # db_alert.picture_id でpictureテーブルから、pictureを取得
    # {"picture": <picture>}の形式で返す
    # ※型はstring
    res_picture_id = db_alert.picture_id

    return picture_cruds.find_by_id(db, res_picture_id)
