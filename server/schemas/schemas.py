from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class AlertStatus(Enum):
    CAMERA = "CAMERA"
    MP4 = "MP4"


class AlertCreate(BaseModel):
    picture_id: int = Field(example=1)
    status: AlertStatus = Field(example=AlertStatus.CAMERA)


class AlertResponse(BaseModel):
    # picture_id: int = Field(gt=0, example=1)
    picture: str = Field(example="http://example.com/picture.jpg")

    model_config = ConfigDict(from_attributes=True)


class PictureCreate(BaseModel):
    picture: str = Field(example="http://example.com/picture.jpg")


class PictureResponse(BaseModel):
    picture_id: int = Field(gt=0, example=1)
    picture: str = Field(example="http://example.com/picture.jpg")
