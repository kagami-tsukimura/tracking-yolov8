from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class AlertStatus(Enum):
    CAMERA = "CAMERA"
    MP4 = "MP4"


class AlertCreate(BaseModel):
    picture_id: int = Field(example=1)
    status: AlertStatus = Field(example=AlertStatus.CAMERA)


class AlertResponse(BaseModel):
    picture_id: int = Field(gt=0, example=1)

    model_config = ConfigDict(from_attributes=True)
