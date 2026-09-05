from sqlalchemy.ext.asyncio import AsyncSession
from app.services.file_service import FileService
from app.db.session import async_session_maker


async def cleanup_expired_files() -> int:
    async with async_session_maker() as session:
        file_service = FileService()
        return await file_service.cleanup_expired_files(session)


async def run_cleanup_job() -> None:
    try:
        count = await cleanup_expired_files()
        if count > 0:
            print(f"Cleaned up {count} expired files")
    except Exception as e:
        print(f"Cleanup job failed: {e}")