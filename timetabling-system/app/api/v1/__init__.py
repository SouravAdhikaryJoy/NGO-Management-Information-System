from fastapi import APIRouter

from app.api.v1 import auth, catalog, config, imports, schedules, sessions, solve, timetable

router = APIRouter(prefix="/api/v1")
router.include_router(auth.router)
router.include_router(catalog.router)
router.include_router(imports.router)
router.include_router(solve.router)
router.include_router(timetable.router)
router.include_router(schedules.router)
router.include_router(sessions.router)
router.include_router(config.router)
