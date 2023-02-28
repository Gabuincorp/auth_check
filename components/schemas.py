from pydantic import BaseModel, EmailStr


class UserEmail(BaseModel):
    email: EmailStr


class UserPhone(BaseModel):
    phone: str


class User(BaseModel):
    id: int
    uid: str
    user_id: int
    school_id: int
    phone: str
    email: str
    role: str
    email_verified: bool


class ActivateCode(BaseModel):
    phone: str
    code: str


class NewPassword(BaseModel):
    password: str
    confirm_password: str
