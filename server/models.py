from database.database import Base
from schemas.schemas import AlertStatus
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.sql.functions import current_timestamp


class Alert(Base):
    __tablename__ = "alerts"

    alert_id = Column(Integer, primary_key=True)
    picture_id = Column(
        Integer, ForeignKey("pictures.picture_id", ondelete="CASCADE"), nullable=False
    )
    status = Column(Enum(AlertStatus), nullable=False)
    created_at = Column(String, default=current_timestamp())
    updated_at = Column(
        DateTime, default=current_timestamp(), onupdate=current_timestamp()
    )


class Picture(Base):
    __tablename__ = "pictures"

    picture_id = Column(Integer, primary_key=True)
    picture = Column(String, nullable=False)
    created_at = Column(String, default=current_timestamp())
    updated_at = Column(
        DateTime, default=current_timestamp(), onupdate=current_timestamp()
    )
