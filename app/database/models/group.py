from __future__ import annotations
from builtins import str
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.database.models.schedule import Schedule


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)  # "CS-101"
    specialty: Mapped[Optional[str]] = mapped_column(nullable=True)  # "Informatika"
    course: Mapped[Optional[int]] = mapped_column(nullable=True)  # 1, 2, 3 ...

    schedules: Mapped[List["Schedule"]] = relationship(
        back_populates="group", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Group id={self.id} name={self.name!r}>"
