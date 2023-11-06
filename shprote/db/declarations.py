from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

DeclarativeBase = declarative_base()


class User(DeclarativeBase):
    __tablename__ = "users"

    user_id = Column(BIGINT(unsigned=False), primary_key=True, autoincrement=False)
    joined = Column(DateTime(timezone=True), default=func.now())
    last_active = Column(DateTime(timezone=True), default=func.now())

    def __repr__(self):
        return "".format(self.code)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
