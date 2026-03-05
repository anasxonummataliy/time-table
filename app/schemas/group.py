from builtins import str
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class GroupBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, examples=["CS-101"])
    specialty: Optional[str] = Field(None, max_length=100, examples=["Informatika"])
    course: Optional[int] = Field(None, ge=1, le=6, examples=[1])


class GroupCreate(GroupBase):
    pass


class GroupUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    specialty: Optional[str] = Field(None, max_length=100)
    course: Optional[int] = Field(None, ge=1, le=6)


class GroupResponse(GroupBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
