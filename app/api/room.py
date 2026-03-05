from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Room
from app.database.session import get_session
from app.schemas.room import RoomCreate, RoomUpdate, RoomStatusUpdate, RoomResponse

router = APIRouter(prefix="/rooms", tags=["Rooms"])


async def _get_or_404(db: AsyncSession, room_id: int) -> Room:
    result = await db.execute(select(Room).where(Room.id == room_id))
    room = result.scalar_one_or_none()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Room not found"
        )
    return room


@router.get("/", response_model=List[RoomResponse])
async def get_all_rooms(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Room))
    return result.scalars().all()


@router.get("/{room_id}", response_model=RoomResponse)
async def get_room(room_id: int, db: AsyncSession = Depends(get_session)):
    return await _get_or_404(db, room_id)


@router.post("/", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
async def create_room(data: RoomCreate, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Room).where(Room.number == data.number))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A room with this number already exists",
        )
    room = Room(**data.model_dump())
    db.add(room)
    await db.commit()
    await db.refresh(room)
    return room


@router.patch("/{room_id}", response_model=RoomResponse)
async def update_room(
    room_id: int, data: RoomUpdate, db: AsyncSession = Depends(get_session)
):
    room = await _get_or_404(db, room_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(room, field, value)
    await db.commit()
    await db.refresh(room)
    return room


@router.patch("/{room_id}/status", response_model=RoomResponse)
async def update_room_status(
    room_id: int, data: RoomStatusUpdate, db: AsyncSession = Depends(get_session)
):
    """Update room status: active | maintenance | closed"""
    room = await _get_or_404(db, room_id)
    room.status = data.status
    await db.commit()
    await db.refresh(room)
    return room


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room(room_id: int, db: AsyncSession = Depends(get_session)):
    room = await _get_or_404(db, room_id)
    await db.delete(room)
    await db.commit()
