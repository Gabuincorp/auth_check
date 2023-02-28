"""Module for Auth Kyiv ID"""

from fastapi import APIRouter
from starlette.requests import Request
from starlette.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuthError
import time
# Dependencies
from core.configurations import kyiv_settings, errs
from core import security
from apps import crud

kyivID_router = APIRouter()


@kyivID_router.get("/login/{source}")
async def kyiv_auth(request: Request, source: str):
    """Generating URL for Kyiv Auth"""
    redirect_uri = kyiv_settings.redirect_url + f"{source}"
    return await kyiv_settings.oauth.kyiv.authorize_redirect(request, redirect_uri)


@kyivID_router.get("/kyiv/{source}")
async def auth_eschool(request: Request, source: str):
    """Generating tokens for Eschool"""
    start = time.perf_counter()
    data_array = await collect_and_check(request)
    teachers_tokens = []
    other_tokens = []
    for data in data_array:
        if data.get("role") == "teacher":
            teachers_tokens.append(await security.create_access_token(data))
        else:
            other_tokens.append(await security.create_access_token(data))
    if source == "journal":
        tokens = ",".join(teachers_tokens)
        end = time.perf_counter()
        print(end - start)
        return RedirectResponse(url=f"{kyiv_settings.eschool_journal}?token={tokens}")
    if source == "diary":
        tokens = ",".join(other_tokens)
        end = time.perf_counter()
        print(end - start)
        return RedirectResponse(url=f"{kyiv_settings.eschool_diary}?token={tokens}")


async def get_kyiv_data(request: Request):
    """Get Kyiv Token and user info from token"""
    try:
        token = await kyiv_settings.oauth.kyiv.authorize_access_token(request)
        return token.get("userinfo")
    except OAuthError as exc:
        raise errs.CREDENTIALS_EXCEPTION from exc


async def collect_and_check(request: Request):
    """ Checking data from database, checking phone number, collect data that needed.  """
    data_array = []
    kyiv_user = await get_kyiv_data(request)
    phone = kyiv_user["phone_number"]
    if phone.startswith("+"):
        phone = phone[1:]
    else:
        phone = phone
    users = await crud.get_users_by_phone(phone=phone)
    for user in users:
        school_id = user["school_id"]
        school = await crud.get_school(school_id=school_id)
        user_schools = [
            {
                "user_id": str(user["user_id"]),
                "school_id": school_id
            }
        ]
        data = {
            "phone": phone,
            "kiev_id": kyiv_user["jti"],
            "role": user["role"],
            "school_id": school_id,
            "jti": str(user["user_id"]),
            "permissions": user["permissions"],
            "school_name": school["name"],
            "user_schools": user_schools,
        }
        data_array.append(data)

    return data_array
