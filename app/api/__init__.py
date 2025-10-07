from fastapi import APIRouter
from app.conf import settings
from app.core.security import AuthRequired, Permission

global_router = APIRouter(prefix=settings.GLOBAL_ROUTER_PREFIX)

# Register your API routes here


@global_router.get("/test")
async def test(token=AuthRequired(Permission("test:read") | Permission("test:write"))):
    return {"message": "Test endpoint", "user": token.sub}
