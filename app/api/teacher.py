from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Teacher
from app.database.session import get_session
from app.schemas.teacher import TeacherCreate, TeacherUpdate, TeacherResponse

router = APIRouter(prefix="/teachers", tags=["Teachers"])


async def _get_or_404(db: AsyncSession, teacher_id: int) -> Teacher:
    result = await db.execute(select(Teacher).where(Teacher.id == teacher_id))
    teacher = result.scalar_one_or_none()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="O'qituvchi topilmadi"
        )
    return teacher


@router.get("/", response_model=List[TeacherResponse])
async def get_all_teachers(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Teacher))
    return result.scalars().all()


@router.get("/{teacher_id}", response_model=TeacherResponse)
async def get_teacher(teacher_id: int, db: AsyncSession = Depends(get_session)):
    return await _get_or_404(db, teacher_id)


@router.post("/", response_model=TeacherResponse, status_code=status.HTTP_201_CREATED)
async def create_teacher(data: TeacherCreate, db: AsyncSession = Depends(get_session)):
    teacher = Teacher(**data.model_dump())
    db.add(teacher)
    await db.commit()
    await db.refresh(teacher)
    return teacher


@router.patch("/{teacher_id}", response_model=TeacherResponse)
async def update_teacher(
    teacher_id: int, data: TeacherUpdate, db: AsyncSession = Depends(get_session)
):
    teacher = await _get_or_404(db, teacher_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(teacher, field, value)
    await db.commit()
    await db.refresh(teacher)
    return teacher


@router.delete("/{teacher_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_teacher(teacher_id: int, db: AsyncSession = Depends(get_session)):
    teacher = await _get_or_404(db, teacher_id)
    await db.delete(teacher)
    await db.commit()
