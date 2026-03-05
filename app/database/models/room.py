from __future__ import annotations
from builtins import str
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.database.models.schedule import Schedule


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[str] = mapped_column(unique=True, nullable=False)  # "301-A"
    capacity: Mapped[Optional[int]] = mapped_column(nullable=True)  # 60
    room_type: Mapped[Optional[str]] = mapped_column(
        nullable=True
    )  # "Darsxona" | "Lab" | "Auditoriya"
    floor: Mapped[Optional[int]] = mapped_column(nullable=True)  # 3
    status: Mapped[str] = mapped_column(
        nullable=False, default="active", server_default='active'
    )  # "faol" | "tamir" | "yopiq"

    schedules: Mapped[List["Schedule"]] = relationship(
        back_populates="room", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Room id={self.id} number={self.number!r} status={self.status!r}>"
