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

from expiringdict import ExpiringDict
from sqlalchemy.orm import scoped_session
from sqlalchemy.sql import func

from shprote.db import DB_SESSION_FACTORY
from shprote.db.declarations import User
from shprote.log import get_logger

logger = get_logger()


acitive_recently = ExpiringDict(max_len=128, max_age_seconds=28800)


def upsert_user(user_id: int):
    """Update info about last active users

    :param user_id: _description_
    :type user_id: int
    """

    if acitive_recently.get(user_id):  # Using cache not to update too often
        return
    else:
        acitive_recently[user_id] = True

    session = scoped_session(DB_SESSION_FACTORY)

    usr_found = session.query(User).filter(User.user_id == user_id).first()
    if usr_found:
        usr_found.last_active = func.now()
    else:
        usr_found = User(user_id=user_id)
        session.add(usr_found)

    try:
        session.commit()
    except:
        logger.warning(
            "Something went wrong while trying to upsert user visit info. Rolling back..."
        )
        session.rollback()
    finally:
        session.close()


def get_user_id_list():
    session = scoped_session(DB_SESSION_FACTORY)
    id_list = session.query(User.user_id).distinct()
    session.close()
    return id_list


def remove_user_by_id(user_id: int):
    session = scoped_session(DB_SESSION_FACTORY)

    session.query(User).filter(User.user_id == user_id).delete()

    try:
        session.commit()
    except:
        logger.warning(
            "Something went wrong while trying to upsert user visit info. Rolling back..."
        )
        session.rollback()
    finally:
        session.close()
