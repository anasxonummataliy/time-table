from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict, field_validator


RoomStatus = Literal["active", "maintenance", "closed"]

# Normalizes any legacy Uzbek values still present in the database
_STATUS_MAP = {
    "active": "active",
    "maintenance": "maintenance",
    "closed": "closed",
    "faol": "active",
    "tamir": "maintenance",
    "yopiq": "closed",
}


class RoomBase(BaseModel):
    number: str = Field(..., min_length=1, max_length=20, examples=["301-A"])
    capacity: Optional[int] = Field(None, ge=1, le=1000, examples=[60])
    room_type: Optional[str] = Field(None, max_length=50, examples=["Darsxona"])
    floor: Optional[int] = Field(None, ge=1, le=30, examples=[3])
    status: RoomStatus = Field(default="active", examples=["active"])


class RoomCreate(RoomBase):
    pass


class RoomUpdate(BaseModel):
    number: Optional[str] = Field(None, min_length=1, max_length=20)
    capacity: Optional[int] = Field(None, ge=1, le=1000)
    room_type: Optional[str] = Field(None, max_length=50)
    floor: Optional[int] = Field(None, ge=1, le=30)
    status: Optional[RoomStatus] = None


class RoomStatusUpdate(BaseModel):
    status: RoomStatus = Field(..., examples=["maintenance"])


class RoomResponse(RoomBase):
    model_config = ConfigDict(from_attributes=True)

    id: int

    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, v: str) -> str:
        """Converts legacy Uzbek status values to English equivalents."""
        return _STATUS_MAP.get(str(v).lower(), "active")
