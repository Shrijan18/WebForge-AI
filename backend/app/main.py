from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.generate import router as generate_router
from app.routes.projects import router as projects_router
from app.config.config import settings

from app.routes.run import router as run_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Autonomous Web Development Platform"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generate_router)
app.include_router(projects_router)


@app.get("/")
def home():
    return {
        "message": "Welcome to WebForge AI 🚀"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


app.include_router(run_router)