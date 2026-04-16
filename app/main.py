from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager

from app.config.database import connect_db, close_db
from app.controllers.auth_controller import router as auth_router
from app.controllers.doctor_controller import router as doctor_router
from app.controllers.queue_controller import router as queue_router
from app.controllers.ai_controller import router as ai_router
from app.controllers.notification_controller import router as notification_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await close_db()

app = FastAPI(
    title="Smart Doctor Finder API",
    description="Backend with AI Assistant",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(doctor_router)
app.include_router(queue_router)
app.include_router(ai_router)
app.include_router(notification_router)

app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/")
async def read_index():
    return FileResponse("index.html")

@app.get("/api/health")
async def health():
    return {"status": "OK", "message": "Smart Doctor API Running 🚀"}