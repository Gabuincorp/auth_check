from fastapi import APIRouter, HTTPException
from jose import jwt
from core.configurations import security_settings
from jose.exceptions import JWTError

api_router = APIRouter()


@api_router.get("/token={token}")
async def check_token(token: str):
    try:
        jwt.decode(
            token=token,
            algorithms="HS256",
            key=security_settings.eschool_secret
        )
        return {"Ok??": "Yes its ok"}

    except JWTError as err:
        raise HTTPException(status_code=404, detail=str(err))