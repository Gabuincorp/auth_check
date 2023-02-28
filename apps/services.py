import re
from smtplib import SMTP
from fastapi import HTTPException
from jose import jwt
from core.configurations import eschool_mail_server

from apps import crud
from core import security
from components import schemas
from core.configurations import security_settings
from apps.crud import *
from core.security import Hasher


async def verify_check(username: str, password: str):
    """Checking if user exist in database and password is correct"""
    users = await get_users_by_phone(phone=username) or await get_users_by_email(email=username)
    for user in users:
        if not user:
            return False
        if not await Hasher.verify_password(password, user["bcrypt"]):
            if not await Hasher.verify_password(password, user["reset_bcrypt"]):
                return False
    return users


async def get_school_dsn(school_id: int):
    school = await crud.get_school(school_id)
    dsn = re.sub("[()]", "", school["dsn"].replace("tcp", ""))
    return dsn


def send_mail_message(recipients, message):
    login = eschool_mail_server.login_data
    mail_from = login.get("user")
    connection = eschool_mail_server.connection_data
    server = SMTP(**connection)
    server.starttls()
    server.ehlo()
    server.login(**login)
    server.sendmail(from_addr=mail_from, to_addrs=recipients, msg=message.encode("utf-8"))
    server.quit()
    print("Mail was send")


async def check_hash(school: str, hash: str, request: schemas.ActivateCode):
    """Checking if Hash exist and data that user input is correct """
    dsn = await get_school_dsn(int(school))
    info = await crud.get_confirm_hash(
        dsn=dsn,
        hash=hash
    )
    if not info:
        raise HTTPException(status_code=500, detail="User not found")
    if info["phone"] != request.phone or info["code"] != request.code:
        raise HTTPException(status_code=404, detail="Code or last 5 numbers of phone wrong")
    token = await security.create_access_token(
        {
            "email": info["email"],
            "dsn": dsn
        }
    )
    return token


async def create_new_password(token: str, request: schemas.NewPassword):
    """Create new password and update that email and hash now confirmed"""
    payload = jwt.decode(
        token=token,
        algorithms="HS256",
        key=security_settings.eschool_secret
    )
    user = await crud.get_user_by_email(payload.get("email"))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    password = await Hasher.get_password_hash(password=request.password)
    await crud.update_password(email=payload.get("email"), password=password)
    await crud.update_confirm(email=payload.get("email"))
    await crud.update_hash(dsn=payload.get("dsn"), email=payload.get("email"))
