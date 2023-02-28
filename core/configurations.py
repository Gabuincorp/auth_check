from pathlib import Path
import yaml
from pydantic import BaseSettings
from starlette.config import Config
from authlib.integrations.starlette_client import OAuth
from fastapi import HTTPException
from fastapi import status

db_config_path = Path("./core") / "configurations.yaml"

with open(db_config_path, "r", encoding="utf-8") as f:
    data = yaml.safe_load(f)


class ServerSettings(BaseSettings):
    server_data = data["server"]
    server_host: str = data["server"]["server_host"]
    server_port: int = data["server"]["server_port"]


class DataBaseSettings(BaseSettings):
    database_master = data["database_master"]


class EschoolMailServer:
    email_server = data["email_server"]
    service_url = data["email_server"]["service_url"]

    connection_data = {
        "host": data["email_server"]["smtp_host"],
        "port": data["email_server"]["smtp_port"]
    }

    login_data = {
        "user": data["email_server"]["smtp_user"],
        "password": data["email_server"]["smtp_password"]
    }


class CelerySettings:
    celery_data = data["celery"]
    celery_broker = data["celery"]["celery_broker_url"]
    celery_backend = data["celery"]["celery_backend_result"]


class SecuritySettings:
    security_data = data["security"]
    eschool_secret = data["security"]["eschool_secret"]
    my_secret_key = data["security"]["my_secret_key"]
    token_expire_time = data["security"]["access_token_expire"]
    algorithm = data["security"]["algorithm"]


class KyivSettings:
    kyiv_data = data["kyiv"]
    kyiv_metadata_url = data["kyiv"]["kyiv_metadata_url"]
    kyiv_client_secret = data["kyiv"]["kyiv_client_secret"]
    kyiv_client_id = data["kyiv"]["kyiv_client_id"]
    redirect_url = data["kyiv"]["redirect_url"]
    eschool_journal = data["kyiv"]["journal_eschool_test"]
    eschool_diary = data["kyiv"]["diary_eschool_test"]

    if kyiv_client_secret is None or kyiv_client_id is None:
        raise f"Missing Data {kyiv_client_secret} or {kyiv_client_id}"
    config_data = {"KYIV_CLIENT_ID": kyiv_client_id, 'KYIV_CLIENT_SECRET': kyiv_client_secret}
    config = Config(environ=config_data)
    oauth = OAuth(config)

    oauth.register(
        name="kyiv",
        server_metadata_url=kyiv_metadata_url,
        client_kwargs={"scope": "openid profile email phone"},
    )


class Exceptions:
    CREDENTIALS_EXCEPTION = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": 'Bearer'},
    )


database_settings = DataBaseSettings()
eschool_mail_server = EschoolMailServer()
server_settings = ServerSettings()
security_settings = SecuritySettings()
celery_settings = CelerySettings()
kyiv_settings = KyivSettings()
errs = Exceptions()
