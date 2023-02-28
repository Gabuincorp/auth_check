from sqlalchemy import insert, update
# Dependencies
from components import models
from core.data_base import master_database
from core.data_base import async_connect


async def get_users_by_email(email: str):
    """Get all users from Master DB by email"""
    query = await master_database.fetch_all(models.user.select().where(models.user.c.email == email))
    return query


async def get_users_by_phone(phone: str):
    """Get all users from Master DB by phone"""
    query = await master_database.fetch_all(models.user.select().where(models.user.c.phone == phone))
    return query


async def get_user_by_email(email: str):
    """Get  user from Master DB by email"""
    query = await master_database.fetch_one(models.user.select().where(models.user.c.email == email))
    return query


async def get_user_by_phone(phone: str):
    """Get all users from Master DB by phone"""
    query = await master_database.fetch_one(models.user.select().where(models.user.c.phone == phone))
    return query


async def get_school(school_id: int):
    """Get school from Master DB by ID"""
    query = await master_database.fetch_one(models.school.select().where(models.school.c.id == school_id))
    return query


async def first_login_timestamp(email: str, login_time: int):
    """Update first login for user in Master DB"""
    query = models.user.update().where(models.user.c.email == email).values(first_login=login_time)
    await master_database.execute(query)


async def last_login_timestamp(email: str, login_time: int):
    """Update last login for user in Master DB"""
    query = models.user.update().where(models.user.c.email == email).values(last_login=login_time)
    await master_database.execute(query)


async def reset_bcrypt_update(phone: str, data: dict):
    """Update reset bcrypt for user in Master DB"""
    await master_database.execute(models.user.update().where(models.user.c.phone == phone).values(data))


async def reset_bcrypt_to_bcrypt(email: str, bcrypt_data: dict):
    """ Reset bcrypt became bcrypt for user in Master DB """
    await master_database.execute(models.user.update().where(models.user.c.email == email).values(bcrypt_data))


async def create_email_code(dsn: str, data: dict):
    """Create new entry for email confirmation in School DB"""
    database = async_connect(dsn)
    await database.connect()
    await database.execute(insert(models.email_confirmation).values(data))
    await database.disconnect()


async def update_email_code(dsn: str, data: dict, email: str):
    """Update  email confirmation date in School DB"""
    database = async_connect(dsn)
    await database.connect()
    await database.execute(
        update(models.email_confirmation).where(models.email_confirmation.c.email == email).values(data))
    await database.disconnect()


async def get_confirm_email(dsn: str, email: str):
    """Get email confirmation info for School DB by email"""
    database = async_connect(dsn)
    await database.connect()
    query = await database.fetch_one(
        models.email_confirmation.select().where(models.email_confirmation.c.email == email))
    await database.disconnect()
    return query


async def get_confirm_hash(dsn: str, hash: str):
    """Get email confirmation info for School DB by hash"""
    database = async_connect(dsn)
    await database.connect()
    query = await database.fetch_one(
        models.email_confirmation.select().where(models.email_confirmation.c.hash == hash))
    await database.disconnect()
    return query


async def update_password(email: str, password: str):
    """Update bcrypt for user in master BD"""
    await master_database.execute(models.user.update().where(models.user.c.email == email).values(bcrypt=password))


async def update_confirm(email: str):
    """Update email confirmation for user in Master DB"""
    await master_database.execute(models.user.update().where(models.user.c.email == email).values(email_verified=1))


async def update_hash(dsn: str, email: str):
    """Update confirmation in School DB"""
    database = async_connect(dsn)
    await database.connect()
    query = models.email_confirmation.update().where(models.email_confirmation.c.email == email).values(confirmed=1)
    await database.execute(query)
    await database.disconnect()
