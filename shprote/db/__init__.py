from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine, URL
import os

from shprote.config import get_config
from shprote.db.declarations import *

config = get_config()

DATABASE = {}
DB_ENGINE = None

if "CLEARDB_DATABASE_URL" in os.environ:
    DATABASE = os.environ["CLEARDB_DATABASE_URL"].replace(
        "?reconnect=true", "")
    DB_ENGINE = create_engine(DATABASE, echo=config["main"]["debug"])
else:
    DATABASE = config["database"]
    DB_ENGINE = create_engine(URL.create(**DATABASE),
                              echo=config["main"]["debug"])

DeclarativeBase.metadata.create_all(DB_ENGINE)
DB_SESSION = sessionmaker(bind=DB_ENGINE)()
