# Shprote bot - Standardized Hanyu (Chinese) PROnunciation TEster
# Copyright (C) 2023, 2024 Alexander Rusakevich

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os

from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker

from shprote.config import get_config
from shprote.db.declarations import DeclarativeBase

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
    "charset": "utf8mb4",
    "collation": "utf8mb4_general_ci",
}

if "JAWSDB_URL" in os.environ:
    DATABASE = os.environ["JAWSDB_URL"]
    DB_ENGINE = create_engine(
        DATABASE, echo=config["main"]["debug"], connect_args=connect_args, **db_options
    )
elif "CLEARDB_DATABASE_URL" in os.environ:
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
