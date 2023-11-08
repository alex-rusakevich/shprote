import os

from sqlalchemy import URL, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from shprote.config import get_config
from shprote.db.declarations import *

config = get_config()

DATABASE = {}
DB_ENGINE = None

db_options = config["database"]["options"]
db_options = {
    "pool_pre_ping": db_options["pre-ping"],
    "pool_recycle": db_options["recycle"],
}

connect_args = {
    "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
    "charset": "utf8",
    "collation": "utf8_general_ci",
}

if "CLEARDB_DATABASE_URL" in os.environ:
    DATABASE = os.environ["CLEARDB_DATABASE_URL"].replace("?reconnect=true", "")
    DB_ENGINE = create_engine(
        DATABASE, echo=config["main"]["debug"], connect_args=connect_args, **db_options
    )
else:
    DATABASE = config["database"]["connection"]
    DB_ENGINE = create_engine(
        URL.create(**DATABASE),
        echo=config["main"]["debug"],
        connect_args=connect_args,
        **db_options
    )

DeclarativeBase.metadata.create_all(DB_ENGINE)
DB_SESSION_FACTORY = sessionmaker(bind=DB_ENGINE)
DB_SESSION = DB_SESSION_FACTORY()
