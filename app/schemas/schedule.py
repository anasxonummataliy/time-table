from builtins import str
from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict

from app.schemas.group import GroupResponse
from app.schemas.teacher import TeacherResponse
from app.schemas.room import RoomResponse


DAY_CHOICES = Literal[
    "Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba"
]


WEEK_TYPE = Literal["odd", "even"]

LESSON_TYPE = Literal["Ma'ruza", "Amaliyot", "Lab", "Seminar"]


LESSON_TIMES: dict[int, str] = {
    1: "09:00 – 10:20",
    2: "10:30 – 11:50",
    3: "12:00 – 13:20",
    4: "14:20 – 15:40",
    5: "15:50 – 17:10",
    6: "17:20 – 18:40",
}


class ScheduleBase(BaseModel):
    group_id: int = Field(..., gt=0)
    teacher_id: int = Field(..., gt=0)
    room_id: int = Field(..., gt=0)

    day_of_week: DAY_CHOICES
    lesson_number: int = Field(..., ge=1, le=6, examples=[1])
    week_type: Optional[WEEK_TYPE] = Field(
        None,
        description="'odd' = toq hafta | 'even' = juft hafta | null = har hafta",
    )

    subject: str = Field(..., min_length=1, max_length=100, examples=["Fizika"])
    lesson_type: Optional[LESSON_TYPE] = Field(None, examples=["Ma'ruza"])


class ScheduleCreate(ScheduleBase):
    pass


class ScheduleUpdate(BaseModel):
    group_id: Optional[int] = Field(None, gt=0)
    teacher_id: Optional[int] = Field(None, gt=0)
    room_id: Optional[int] = Field(None, gt=0)

    day_of_week: Optional[DAY_CHOICES] = None
    lesson_number: Optional[int] = Field(None, ge=1, le=6)
    week_type: Optional[WEEK_TYPE] = None

    subject: Optional[str] = Field(None, min_length=1, max_length=100)
    lesson_type: Optional[LESSON_TYPE] = None


class ScheduleResponse(ScheduleBase):
    """Oddiy response — faqat ID lar bilan (tez)"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    lesson_time: str = ""

    @model_validator(mode="after")
    def fill_lesson_time(self) -> "ScheduleResponse":
        self.lesson_time = LESSON_TIMES.get(self.lesson_number, "")
        return self


class ScheduleDetailResponse(BaseModel):
    """To'liq response — nested group, teacher, room obyektlari bilan"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    day_of_week: str
    lesson_number: int
    lesson_time: str = ""
    week_type: Optional[str]
    subject: str
    lesson_type: Optional[str]

    group: GroupResponse
    teacher: TeacherResponse
    room: RoomResponse

    @model_validator(mode="after")
    def fill_lesson_time(self) -> "ScheduleDetailResponse":
        self.lesson_time = LESSON_TIMES.get(self.lesson_number, "")
        return self
