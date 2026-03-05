from __future__ import annotations
from builtins import str
from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.database.models.group import Group
    from app.database.models.teacher import Teacher
    from app.database.models.room import Room


LESSON_TIMES: dict[int, str] = {
    1: "09:00 – 10:20",
    2: "10:30 – 11:50",
    3: "12:00 – 13:20",
    4: "14:20 – 15:40",
    5: "15:50 – 17:10",
    6: "17:20 – 18:40",
}

DAYS = ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba"]


class Schedule(Base):
    __tablename__ = "schedules"

    id: Mapped[int] = mapped_column(primary_key=True)

    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teachers.id"), nullable=False)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), nullable=False)

    day_of_week: Mapped[str] = mapped_column(nullable=False)
    lesson_number: Mapped[int] = mapped_column(nullable=False)
    week_type: Mapped[Optional[str]] = mapped_column(nullable=True)

    subject: Mapped[str] = mapped_column(nullable=False)  # "Fizika"
    lesson_type: Mapped[Optional[str]] = mapped_column(nullable=True)

    group: Mapped["Group"] = relationship(back_populates="schedules")
    teacher: Mapped["Teacher"] = relationship(back_populates="schedules")
    room: Mapped["Room"] = relationship(back_populates="schedules")

    __table_args__ = (
        # Xona: bir vaqtda bir dars
        UniqueConstraint(
            "room_id",
            "day_of_week",
            "lesson_number",
            "week_type",
            name="uq_room_slot",
        ),
        # O'qituvchi: bir vaqtda bir dars
        UniqueConstraint(
            "teacher_id",
            "day_of_week",
            "lesson_number",
            "week_type",
            name="uq_teacher_slot",
        ),
        # Guruh: bir vaqtda bir dars
        UniqueConstraint(
            "group_id",
            "day_of_week",
            "lesson_number",
            "week_type",
            name="uq_group_slot",
        ),
        # lesson_number 1-6 orasida bo'lishi shart
        CheckConstraint(
            "lesson_number BETWEEN 1 AND 6",
            name="ck_lesson_number_range",
        ),
        # week_type faqat ruxsat etilgan qiymatlar
        CheckConstraint(
            "week_type IN ('odd', 'even') OR week_type IS NULL",
            name="ck_week_type_values",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<Schedule id={self.id} "
            f"{self.day_of_week} {self.lesson_number}-juft "
            f"| {self.subject} "
            f"| week={self.week_type!r}>"
        )
