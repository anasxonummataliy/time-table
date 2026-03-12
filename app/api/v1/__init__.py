from fastapi import APIRouter

from app.api.v1.group import router as group_router
from app.api.v1.teacher import router as teacher_router
from app.api.v1.room import router as room_router
from app.api.v1.schedule import router as schedule_router

routers = APIRouter(prefix="/api")

routers.include_router(group_router)
routers.include_router(teacher_router)
routers.include_router(room_router)
routers.include_router(schedule_router)
