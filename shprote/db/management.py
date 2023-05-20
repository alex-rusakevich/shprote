from sqlalchemy.sql import func
from sqlalchemy.orm import scoped_session

from shprote.db import DB_SESSION_FACTORY
from shprote.db.declarations import User
from shprote.log import get_logger

logger = get_logger()


def upsert_user(user_id: int):
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
            "Something went wrong while trying to upsert user visit info. Rolling back...")
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
            "Something went wrong while trying to upsert user visit info. Rolling back...")
        session.rollback()
    finally:
        session.close()
