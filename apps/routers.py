from fastapi import APIRouter
from apps.HtmlPages import HtmlPages_router
from apps.auth import auth_router
from apps.KyivID import kyivID_router
from apps.api import api_router

apps_router = APIRouter()
apps_router.include_router(HtmlPages_router, prefix="", tags=["HtmlPages"])
apps_router.include_router(auth_router, prefix="/auth", tags=["auth"])
apps_router.include_router(kyivID_router, prefix="/oauth", tags=["kyiv"])
apps_router.include_router(api_router, prefix="/api", tags=["token"])

# Test part
# ----------------------------------------------
