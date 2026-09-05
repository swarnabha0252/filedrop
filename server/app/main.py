from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.api.router import api_router
from app.db.session import init_db, close_db
from app.services.cleanup_service import run_cleanup_job
import asyncio


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    cleanup_task = asyncio.create_task(periodic_cleanup())
    yield
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass
    await close_db()


async def periodic_cleanup():
    while True:
        await asyncio.sleep(settings.CLEANUP_INTERVAL_SECONDS)
        await run_cleanup_job()


app = FastAPI(
    title="FileDrop API",
    description="Temporary file sharing API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.exception_handler(413)
async def payload_too_large_handler(request, exc):
    return JSONResponse(
        status_code=413,
        content={"error": {"code": "PAYLOAD_TOO_LARGE", "message": f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE_MB} MB"}},
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "INTERNAL_ERROR", "message": "An internal server error occurred"}},
    )