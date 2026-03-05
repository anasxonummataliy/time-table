from fastapi import APIRouter

from app.api.group import router as group_router
from app.api.teacher import router as teacher_router
from app.api.room import router as room_router
from app.api.schedule import router as schedule_router

routers = APIRouter(prefix="/api")

routers.include_router(group_router)
routers.include_router(teacher_router)
routers.include_router(room_router)
routers.include_router(schedule_router)
