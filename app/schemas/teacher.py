from builtins import str
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, ConfigDict


class TeacherBase(BaseModel):
    full_name: str = Field(
        ..., min_length=2, max_length=150, examples=["Karimov Alisher"]
    )
    subject: str = Field(..., min_length=1, max_length=100, examples=["Matematika"])
    phone: Optional[str] = Field(None, max_length=20, examples=["+998901234567"])
    email: Optional[EmailStr] = Field(None, examples=["karimov@univer.uz"])  # type: ignore


class TeacherCreate(TeacherBase):
    pass


class TeacherUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=150)
    subject: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None  # type: ignore


class TeacherResponse(TeacherBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
