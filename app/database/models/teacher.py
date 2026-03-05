from __future__ import annotations
from builtins import str
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.database.models.schedule import Schedule


class Teacher(Base):
    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(nullable=False)  # "Karimov Alisher"
    subject: Mapped[str] = mapped_column(nullable=False)  # "Matematika"
    phone: Mapped[Optional[str]] = mapped_column(nullable=True)
    email: Mapped[Optional[str]] = mapped_column(nullable=True)

    schedules: Mapped[List["Schedule"]] = relationship(
        back_populates="teacher", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Teacher id={self.id} name={self.full_name!r}>"
