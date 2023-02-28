"""
Module for HTML pages

"""
import re
from datetime import datetime
from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates

# Dependencies
from starlette.responses import JSONResponse, RedirectResponse
from apps import auth
from components import forms
from apps import crud, services

#
templates = Jinja2Templates(directory="./templates/pages")
HtmlPages_router = APIRouter()


@HtmlPages_router.get("/")
async def home(request: Request, msg: str = None):
    """Home page"""
    return templates.TemplateResponse("homepage.html", {"request": request, "msg": msg})


@HtmlPages_router.get("/login")
async def login(request: Request):
    """Login page"""
    return templates.TemplateResponse("login.html", {"request": request})


@HtmlPages_router.post("/login")
async def login(request: Request):
    """Login page with checking form"""
    form = forms.LoginForm(request)
    await form.load_data()
    if await form.is_valid():
        try:
            tokens = await auth.login(request=form)
            return JSONResponse(tokens)
        except HTTPException as err:
            form.__dict__.update(msg="")
            form.__dict__.get("errors").append(f"{err.detail}")
        return templates.TemplateResponse("login.html", form.__dict__)
    return templates.TemplateResponse("login.html", form.__dict__)


@HtmlPages_router.get("/reset-password")
async def reset_password(request: Request):
    """Reset Password Page"""
    return templates.TemplateResponse("reset-password.html", {"request": request})


@HtmlPages_router.post("/reset-password")
async def reset_password(request: Request):
    """Reset Password with checking form"""
    form = forms.ResetPasswordForm(request)
    await form.load_data()
    if await form.phone_is_valid():
        try:
            form.__dict__.update(msg=f"Code was send on email:{form.phone}")
            await auth.reset_password(request=form)
            return templates.TemplateResponse("reset-password.html", form.__dict__)
        except HTTPException as err:
            form.__dict__.update(msg="")
            form.__dict__.get("errors").append(f"{err.detail}")
        return templates.TemplateResponse("reset-password.html", form.__dict__)


@HtmlPages_router.get("/email-verify")
async def verify_email(request: Request):
    """Send Email confirmation code page"""
    return templates.TemplateResponse("send-code.html", {"request": request})


@HtmlPages_router.post("/email-verify")
async def verify_email(request: Request):
    """Send Email confirmation code page with checking form"""
    form = forms.UserEmail(request)
    await form.load_data()
    if await form.email_is_valid():
        try:
            form.__dict__.update(msg=f"Please check your email {form.email} for info")
            await auth.verify_code(request=form)
            return templates.TemplateResponse("send-code.html", form.__dict__)
        except HTTPException as err:
            form.__dict__.update(msg="")
            form.__dict__.get("errors").append(f"{err.detail}")
            return templates.TemplateResponse("send-code.html", form.__dict__)


@HtmlPages_router.get("/email-activate/")
async def activate_email(school: str, hash: str, request: Request):
    """Email activation page """
    dsn = await services.get_school_dsn(int(school))
    info = await crud.get_confirm_hash(dsn=dsn, hash=hash)
    if info is None:
        raise HTTPException(status_code=404, detail="Token Expired")
    if info["confirmed"] >= 1:
        raise HTTPException(status_code=404, detail="Token Expired")
    now = datetime.timestamp(datetime.now().replace(second=0, microsecond=0))
    left = (info["expires"] - now)
    if left < 0:
        raise HTTPException(status_code=404, detail="Token Expired")
    return templates.TemplateResponse("activate-page.html", {"request": request})


@HtmlPages_router.post("/email-activate/", response_class=RedirectResponse)
async def activate_email(school: str, hash: str, request: Request):
    """Email activation page with checking form """
    form = forms.ActivateCode(request)
    await form.load_data()
    if await form.is_valid():
        try:
            form.__dict__.update(msg="Success")
            token = await services.check_hash(school=school, hash=hash, request=form)
            return f"/new/password?token={token}"
        except HTTPException as err:
            form.__dict__.update(msg="")
            form.__dict__.get("errors").append(f"{err.detail}")
        return templates.TemplateResponse("activate-page.html", form.__dict__)
    return templates.TemplateResponse("activate-page.html", form.__dict__)


@HtmlPages_router.get("/new/password")
async def create_new_password(request: Request):
    """New password Page"""
    return templates.TemplateResponse("create_password.html", {"request": request})


@HtmlPages_router.post("/new/password", response_class=RedirectResponse)
async def create_new_password(token: str, request: Request):
    """New password with checking form"""
    form = forms.NewPassword(request)
    await form.load_data()
    if await form.is_valid():
        try:
            form.__dict__.update(msg="Password Updated")
            await services.create_new_password(token=token, request=form)
            return f"/login"
        except HTTPException as err:
            form.__dict__.update(msg="")
            form.__dict__.get("errors").append(f"{err.detail}")
        return templates.TemplateResponse("create_password.html", form.__dict__)
    return templates.TemplateResponse("create_password.html", form.__dict__)
