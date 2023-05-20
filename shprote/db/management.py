from sqlalchemy.sql import func

from shprote.db import DB_SESSION
from shprote.db.declarations import User


def upsert_user(user_id: int):
    usr_found = DB_SESSION.query(User).filter(User.user_id == user_id).first()
    if usr_found:
        usr_found.last_active = func.now()
    else:
        usr_found = User(user_id=user_id)
        DB_SESSION.add(usr_found)
    DB_SESSION.commit()
