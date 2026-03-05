from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Group
from app.database.session import get_session
from app.schemas.group import GroupCreate, GroupUpdate, GroupResponse

router = APIRouter(prefix="/groups", tags=["Groups"])


async def _get_or_404(db: AsyncSession, group_id: int) -> Group:
    result = await db.execute(select(Group).where(Group.id == group_id))
    group = result.scalar_one_or_none()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Guruh topilmadi"
        )
    return group


@router.get("/", response_model=List[GroupResponse])
async def get_all_groups(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Group))
    return result.scalars().all()


@router.get("/{group_id}", response_model=GroupResponse)
async def get_group(group_id: int, db: AsyncSession = Depends(get_session)):
    return await _get_or_404(db, group_id)


@router.post("/", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
async def create_group(data: GroupCreate, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Group).where(Group.name == data.name))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu nomli guruh allaqachon mavjud",
        )
    group = Group(**data.model_dump())
    db.add(group)
    await db.commit()
    await db.refresh(group)
    return group


@router.patch("/{group_id}", response_model=GroupResponse)
async def update_group(
    group_id: int, data: GroupUpdate, db: AsyncSession = Depends(get_session)
):
    group = await _get_or_404(db, group_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(group, field, value)
    await db.commit()
    await db.refresh(group)
    return group


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(group_id: int, db: AsyncSession = Depends(get_session)):
    group = await _get_or_404(db, group_id)
    await db.delete(group)
    await db.commit()
