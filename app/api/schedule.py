from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, and_, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.database.models import Group, Room, Schedule, Teacher
from app.database.session import get_session
from app.schemas.schedule import (
    ScheduleCreate,
    ScheduleDetailResponse,
    ScheduleResponse,
    ScheduleUpdate,
)

router = APIRouter(prefix="/schedules", tags=["Schedules"])


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _get_or_404(db: AsyncSession, schedule_id: int) -> Schedule:
    result = await db.execute(select(Schedule).where(Schedule.id == schedule_id))
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Jadval topilmadi")
    return schedule


async def _check_fk_exist(db: AsyncSession, data: ScheduleCreate | ScheduleUpdate) -> None:
    checks = [
        ("group_id",   Group,   "Guruh"),
        ("teacher_id", Teacher, "O'qituvchi"),
        ("room_id",    Room,    "Xona"),
    ]
    for attr, model, label in checks:
        fk_id = getattr(data, attr, None)
        if fk_id is not None:
            result = await db.execute(select(model).where(model.id == fk_id))
            if not result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"{label} topilmadi (id={fk_id})",
                )


def _week_conflict_condition(week_type: Optional[str]):
    """
    NULL hafta → har hafta demak → toq va juft hafta bilan ham conflict.
    Toq/juft hafta → faqat bir-biri va NULL bilan conflict.
    """
    if week_type is None:
        # NULL kelayotgan bo'lsa: NULL, odd, even hammasi bilan conflict
        return True  # faqat day + lesson tekshirish kifoya
    else:
        # odd/even kelayotgan bo'lsa: NULL yoki o'zi bilan conflict
        from sqlalchemy import or_
        return or_(
            Schedule.week_type == None,   # noqa: E711
            Schedule.week_type == week_type
        )


async def _check_conflicts(
    db: AsyncSession,
    day_of_week: str,
    lesson_number: int,
    week_type: Optional[str],
    room_id: int,
    teacher_id: int,
    group_id: int,
    exclude_id: Optional[int] = None,
) -> None:
    """
    Uch turdagi conflict tekshiradi:
      1. Xona: bir vaqtda bir xonada faqat bitta dars
      2. O'qituvchi: bir vaqtda bitta darsda
      3. Guruh: bir vaqtda bitta darsda
    NULL week_type = har hafta = toq va juft bilan ham toqnashadi
    """

    base = and_(
        Schedule.day_of_week == day_of_week,
        Schedule.lesson_number == lesson_number,
    )

    # week_type conflict sharti
    if week_type is None:
        # yangi dars har hafta → barcha week_type lar bilan toqnashadi
        week_cond = True
    else:
        # yangi dars odd/even → NULL (har hafta) yoki o'zi bilan toqnashadi
        week_cond = or_(
            Schedule.week_type == None,   # noqa: E711
            Schedule.week_type == week_type,
        )

    async def _conflict(extra_cond, label: str):
        stmt = select(Schedule).where(and_(base, week_cond, extra_cond))
        if exclude_id:
            stmt = stmt.where(Schedule.id != exclude_id)
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"{label}: {existing.day_of_week}, {existing.lesson_number}-juft"
                       f"{' ('+('toq' if existing.week_type=='odd' else 'juft')+' hafta)' if existing.week_type else ''}",
            )

    await _conflict(Schedule.room_id    == room_id,    "Bu xonada ushbu vaqtda allaqachon dars bor")
    await _conflict(Schedule.teacher_id == teacher_id, "Bu o'qituvchi ushbu vaqtda boshqa darsda band")
    await _conflict(Schedule.group_id   == group_id,   "Bu guruhda ushbu vaqtda allaqachon dars bor")


def _with_relations(stmt):
    return stmt.options(
        joinedload(Schedule.group),
        joinedload(Schedule.teacher),
        joinedload(Schedule.room),
    )


# ── GET /schedules/ ───────────────────────────────────────────────────────────

@router.get("/", response_model=List[ScheduleDetailResponse])
async def get_schedules(
    group_id:    Optional[int] = Query(None),
    teacher_id:  Optional[int] = Query(None),
    room_id:     Optional[int] = Query(None),
    day_of_week: Optional[str] = Query(None),
    week_type:   Optional[str] = Query(None),
    db: AsyncSession = Depends(get_session),
):
    stmt = _with_relations(select(Schedule))
    if group_id:    stmt = stmt.where(Schedule.group_id    == group_id)
    if teacher_id:  stmt = stmt.where(Schedule.teacher_id  == teacher_id)
    if room_id:     stmt = stmt.where(Schedule.room_id     == room_id)
    if day_of_week: stmt = stmt.where(Schedule.day_of_week == day_of_week)
    if week_type:   stmt = stmt.where(Schedule.week_type   == week_type)
    result = await db.execute(stmt)
    return result.scalars().all()


# ── GET /schedules/{id} ───────────────────────────────────────────────────────

@router.get("/{schedule_id}", response_model=ScheduleDetailResponse)
async def get_schedule(schedule_id: int, db: AsyncSession = Depends(get_session)):
    stmt = _with_relations(select(Schedule).where(Schedule.id == schedule_id))
    result = await db.execute(stmt)
    s = result.scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Jadval topilmadi")
    return s


# ── POST /schedules/ ──────────────────────────────────────────────────────────

@router.post("/", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_schedule(data: ScheduleCreate, db: AsyncSession = Depends(get_session)):
    await _check_fk_exist(db, data)
    await _check_conflicts(
        db,
        day_of_week   = data.day_of_week,
        lesson_number = data.lesson_number,
        week_type     = data.week_type,
        room_id       = data.room_id,
        teacher_id    = data.teacher_id,
        group_id      = data.group_id,
    )
    schedule = Schedule(**data.model_dump())
    db.add(schedule)
    try:
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Jadval konflikti yuz berdi")
    await db.refresh(schedule)
    return schedule


# ── PATCH /schedules/{id} ─────────────────────────────────────────────────────

@router.patch("/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: int, data: ScheduleUpdate, db: AsyncSession = Depends(get_session)
):
    schedule = await _get_or_404(db, schedule_id)
    await _check_fk_exist(db, data)

    # Mavjud qiymatlar + yangi qiymatlarni birlashtir
    merged = {
        "day_of_week":   data.day_of_week   or schedule.day_of_week,
        "lesson_number": data.lesson_number or schedule.lesson_number,
        "week_type":     data.week_type     if "week_type" in data.model_fields_set else schedule.week_type,
        "room_id":       data.room_id       or schedule.room_id,
        "teacher_id":    data.teacher_id    or schedule.teacher_id,
        "group_id":      data.group_id      or schedule.group_id,
    }

    await _check_conflicts(db, exclude_id=schedule_id, **merged)

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(schedule, field, value)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Jadval konflikti yuz berdi")
    await db.refresh(schedule)
    return schedule


# ── DELETE /schedules/{id} ────────────────────────────────────────────────────

@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule(schedule_id: int, db: AsyncSession = Depends(get_session)):
    schedule = await _get_or_404(db, schedule_id)
    await db.delete(schedule)
    await db.commit()
