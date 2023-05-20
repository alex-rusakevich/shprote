from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine, URL
import os

from shprote.config import get_config
from shprote.db.declarations import *

config = get_config()

DATABASE = {}
DB_ENGINE = None

db_options = config["database"]["options"]
db_options = {
    "pool_pre_ping": db_options["pre-ping"],
    "pool_recycle": db_options["recycle"]
}

if "CLEARDB_DATABASE_URL" in os.environ:
    DATABASE = os.environ["CLEARDB_DATABASE_URL"].replace(
        "?reconnect=true", "")
    DB_ENGINE = create_engine(
        DATABASE, echo=config["main"]["debug"], **db_options)
else:
    DATABASE = config["database"]["connection"]
    DB_ENGINE = create_engine(URL.create(**DATABASE),
                              echo=config["main"]["debug"], **db_options)

DeclarativeBase.metadata.create_all(DB_ENGINE)
DB_SESSION_FACTORY = sessionmaker(bind=DB_ENGINE)
DB_SESSION = DB_SESSION_FACTORY()
