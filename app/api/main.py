from fastapi import APIRouter

from app.api.routes import items, login, private, users, utils, unitsystems , Projects , tests , template_tests, template_objects
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(items.router)
api_router.include_router(unitsystems.router)
api_router.include_router(Projects.router)
api_router.include_router(tests.router)
api_router.include_router(template_tests.router)
api_router.include_router(template_objects.router)


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
