from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.api.v1 import routers


BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_INDEX = BASE_DIR / "frontend" / "index.html"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    yield
    # shutdown


app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routers)


@app.get("/health")
async def health():
    return {"status": "ok", "docs": "/docs"}


@app.get("/", include_in_schema=False)
async def start():
    return FileResponse(FRONTEND_INDEX)
