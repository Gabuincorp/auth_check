from databases import Database
from urllib.parse import quote

from core.configurations import database_settings

master = database_settings.database_master


def async_connect(dsn):
    driver = "mysql+aiomysql"
    user = dsn.split("@")[0].split(":")
    db = (dsn.split("@")[1])
    login = user[0]
    password = user[1]
    password = quote(password)
    url = f"{driver}://{login}:{password}@{db}"
    print(url)
    database = Database(url, min_size=5, max_size=20)
    return database


master_database = async_connect(master)
