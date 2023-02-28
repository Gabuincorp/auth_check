import uvicorn
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from apps.routers import apps_router
from core.configurations import security_settings, server_settings
from core.data_base import master_database

ALLOWED_HOSTS = ["*"]


def middleware(server):
    server.add_middleware(
        SessionMiddleware,
        secret_key=security_settings.my_secret_key,
    )
    server.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def include_router(server):
    server.include_router(apps_router)


def configure_static(server):
    server.mount("/statics", StaticFiles(directory="statics"), name="statics")


def start_application():
    server = FastAPI()
    include_router(server)
    configure_static(server)
    middleware(server)
    return server


app = start_application()


@app.on_event("startup")
async def startup():
    await master_database.connect()


@app.on_event("shutdown")
async def shutdown():
    await master_database.disconnect()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=server_settings.server_port,
        log_level="info",
        reload=True,
        ssl_keyfile="./cert/localhost-key.pem",
        ssl_certfile="./cert/localhost-cert.pem"
    )
