from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from random import randint
# Dependencies
from core.configurations import security_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Hasher:
    @staticmethod
    async def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    async def get_password_hash(password):
        return pwd_context.hash(password)


async def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=security_settings.token_expire_time)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, security_settings.eschool_secret, algorithm=security_settings.algorithm)
    return encoded_jwt


async def random_numbers(n):
    range_start = 10 ** (n - 1)
    range_end = (10 ** n) - 1
    return randint(range_start, range_end)

# async def create_token(data: dict):
#     access_token_expires = timedelta(minutes=security_settings.token_expire_time)
#     access_token = await create_access_token(data=data, expires_delta=access_token_expires)
#     return access_token
