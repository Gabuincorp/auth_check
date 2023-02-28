"""Module Forms"""
from typing import List, Optional

from fastapi import Request


class LoginForm:
    """Login Form"""

    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.username: Optional[str] = None
        self.password: Optional[str] = None
        self.email: Optional[str] = None

    async def load_data(self):
        """ Load data to form"""
        form = await self.request.form()
        self.username = form.get("phone") or form.get("email")
        self.password = form.get("password")

    async def is_valid(self):
        """Check if form is valid"""
        if not self.username:
            self.errors.append("Phone is required")
        if not self.password or not len(self.password) >= 4:
            self.errors.append("A valid password is required")
        if not self.errors:
            return True
        return False


class UserEmail:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.email: Optional[str] = None

    async def load_data(self):
        """ Load data to form"""
        form = await self.request.form()
        self.email = form.get("email")

    async def email_is_valid(self):
        if not self.email or not (self.email.__contains__("@")):
            self.errors.append("Email is required")
        if not self.errors:
            return True
        return False


class ResetPasswordForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.phone: Optional[str] = None

    async def load_data(self):
        """ Load data to form"""
        form = await self.request.form()
        self.phone = form.get(
            "phone"
        )

    async def phone_is_valid(self):
        if not self.phone:
            self.errors.append("Phone is required")
        if not self.errors:
            return True
        return False


class ActivateCode:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.code: Optional[str] = None
        self.phone: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.code = form.get("code")
        self.phone = form.get("phone")

    async def is_valid(self):
        """Check if form is valid"""
        if not self.phone or not len(self.phone) > 4:
            self.errors.append("Phone is required")
        if not self.code or not len(self.code) > 7:
            self.errors.append("A valid code is required")
        if not self.errors:
            return True
        return False


class NewPassword:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.password: Optional[str] = None
        self.confirm_password: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.password = form.get("password")
        self.confirm_password = form.get("confirm_password")

    async def is_valid(self):
        """Check if form is valid"""
        if not self.password or not len(self.password) >= 8:
            self.errors.append("Password to short")
        if self.password != self.confirm_password:
            self.errors.append("Passwords do not match")
        if not self.errors:
            return True
        return False
