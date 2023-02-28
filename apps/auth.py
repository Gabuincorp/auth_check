from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from secrets import token_urlsafe
from jose import jwt
import re
import time

from apps import celery_worker
from apps import crud, services
from core.configurations import security_settings
from components import schemas
from core import security

auth_router = APIRouter()


@auth_router.post("/login")
async def login(request: OAuth2PasswordRequestForm = Depends()):
    """Create login token"""
    start = time.perf_counter()
    tokens = []
    time_now = int(datetime.timestamp(datetime.now()))
    users = await services.verify_check(username=request.username, password=request.password)
    # print(users)
    if not users:
        raise HTTPException(status_code=401, detail="Incorrect Login or Password")
    for user in users:
        if not user["email_verified"]:
            raise HTTPException(status_code=404, detail="Email not activated")
        school_id = user["school_id"]
        school = await crud.get_school(school_id)
        # school_name = school["name"]
        users_school = [
            {
                "user_id": str(user["user_id"]),
                "school_id": school_id,
            }
        ]
        data = {
            "role": user["role"],
            "school_id": school_id,
            "jti": str(user["user_id"]),
            "permissions": user["permissions"],
            "school_name": school["name"],
            "user_school": users_school,
        }
        token = {
            "token": await security.create_access_token(data=data),
            "refresh_token": await security.create_access_token(data=data),
            "exp": security_settings.token_expire_time,
            "school_id": school_id,
            "school": school["name"]
        }
        tokens.append(token)
        if not user["first_login"]:
            await crud.first_login_timestamp(email=user["email"], login_time=time_now)
        else:
            await crud.last_login_timestamp(email=user["email"], login_time=time_now)
        if user["reset_bcrypt"] is not None:
            bcrypt_data = {
                "bcrypt": user["reset_bcrypt"],
                "reset_bcrypt": None,
                "reset_count": 0
            }
            await crud.reset_bcrypt_to_bcrypt(email=user["email"], bcrypt_data=bcrypt_data)
    end = time.perf_counter()
    print(end - start)
    return tokens


@auth_router.get("/reset-password")
async def reset_password(request: schemas.UserPhone):
    """ Password Reset """
    start = time.perf_counter()
    users = await crud.get_users_by_phone(phone=request.phone)
    code = await security.random_numbers(6)
    reset_bcrypt = await security.Hasher.get_password_hash(str(code))
    if not users:
        raise HTTPException(status_code=404, detail="User not found")
    for user in users:
        if user.reset_count >= 3:
            raise HTTPException(status_code=404, detail="You have exceeded the number of possible attempts")
        reset_count = user.reset_count + 1
        data = {
            "reset_bcrypt": reset_bcrypt,
            "reset_count": reset_count
        }
        await crud.reset_bcrypt_update(phone=request.phone, data=data)
    postman_data = {
        "recipient": users[0].email,
        "subject": "Reset Password",
        "code": code,
    }
    celery_worker.postman_password.delay(data=postman_data)
    end = time.perf_counter()
    print(end - start)


@auth_router.post("/email-verify")
async def verify_code(request: schemas.UserEmail):
    """Create and send email confirmation code """
    start = time.perf_counter()
    data = {
        "code": await security.random_numbers(8),
        "hash": token_urlsafe(24),
        "expires": datetime.timestamp(datetime.now().replace(second=0, microsecond=0) + timedelta(hours=72))
    }
    users = await crud.get_users_by_email(email=request.email)
    if not users:
        raise HTTPException(status_code=401, detail="User not Found")
    for user in users:
        if user["email_verified"]:
            raise HTTPException(status_code=401, detail="Email already verified")
        school = await crud.get_school(school_id=user["school_id"])
        dsn = re.sub("[()]", "", school["dsn"].replace("tcp", ""))
        confirm_info = await crud.get_confirm_email(dsn=dsn, email=request.email)
        if confirm_info:
            await crud.update_email_code(
                dsn=dsn,
                data=data,
                email=request.email
            )
        if not confirm_info:
            data.update(
                {
                    "user_id": user["user_id"],
                    "email": user["email"],
                    "role": user["role"],
                    "phone": user["phone"][-5:],
                    "confirmed": 0
                }
            )
            await crud.create_email_code(dsn=dsn, data=data)
        postman_data = {
            "code": data.get("code"),
            "link": "https://localhost:8000/email-activate/?school={:0}&hash={:1}".format(
                user["school_id"],
                data.get("hash")
            )
        }

        celery_worker.postman_email.delay(
            data=postman_data,
            role=user["role"],
            email=request.email
        )
        end = time.perf_counter()
        print(end - start)
