from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, BigInteger, Table, MetaData, DateTime
from sqlalchemy.dialects.mysql import TINYTEXT, TEXT, TINYINT, CHAR
from sqlalchemy.orm import relationship

# Dependencies

master_metadata = MetaData()
school_metadata = MetaData()

user = Table(
    "user",
    master_metadata,
    Column("id", Integer(), primary_key=True, nullable=False),
    Column("uid", String(10), nullable=False, unique=True),
    Column("school_id", Integer(), ForeignKey("school.id"), nullable=False),
    Column("user_id", Integer(), ForeignKey("user.id"), nullable=False),
    Column("role", String(16), nullable=False),
    Column("phone", String(16), default=None),
    Column("email", String(320), default=None),
    Column("email_verified", TINYINT(), default=0),
    Column("bcrypt", String(128), default=None),
    Column("reset_bcrypt", String(128), default=None),
    Column("reset_count", Integer(), default=0),
    Column("first_login", BigInteger(), default=None),
    Column("last_login", BigInteger(), default=None),
    Column("permissions", TEXT(), default=None),
    Column("o", Integer(), default=None),
    Column("x", Integer())

)

school = Table(
    "school",
    master_metadata,
    Column("id", Integer(), primary_key=True, nullable=False, index=True),
    Column("name", String(64), nullable=False, default=""),
    Column("dsn", String(128), nullable=False),
    Column("activated", Boolean(), nullable=False),
)

email_confirmation = Table(
    "email_confirmation",
    school_metadata,
    Column("id", Integer(), primary_key=True, nullable=False),
    Column("user_id", Integer(), ForeignKey("user.id"), index=True, nullable=False),
    Column("email", String(320), nullable=False),
    Column("code", CHAR(), nullable=False),
    Column("expires", BigInteger(), nullable=False),
    Column("hash", String(255)),
    Column("role", String(20)),
    Column("phone", String(5)),
    Column("confirmed", Integer(), nullable=False, default=0),
)

school_user = Table(
    "user",
    school_metadata,
    Column("id", Integer(), primary_key=True, nullable=False),
    Column("uid", String(10), unique=True, default=None),
    Column("school_id", Integer(), ForeignKey("school.id"), default=None),
    Column("first_enter", DateTime(), default=None),
    Column("last_activity", DateTime(), default=None),
    Column("phone", String(100), default=None),
    Column("password", String(255), default=None),
    Column("reset_password", String(255), default=None),
    Column("reset_count", Integer(), default=None),
    Column("last_reset", DateTime(), default=None),
    Column("registered", Integer(), default=None),
    Column("role", String(100), default=None),
    Column("email", String(255), default=None),
    Column("avatar_url", String(255), default=None),
    Column("policy_confirmed", Integer(), default=0),
    Column("permissions", TINYTEXT(), default=None),
    Column("fcm_token", TEXT(), default=None),
    Column("client", String(255), default=None),
    Column("self_register", Integer(), default=None),
    Column("add_date", DateTime(), default=0),
    Column("google_ad", Integer(), default=None),
)

