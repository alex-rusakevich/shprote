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

from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import DeclarativeBase as Base
from sqlalchemy.sql import func


class DeclarativeBase(Base):
    __table_prefix__ = "shprote"

    def __init_subclass__(self) -> None:
        self.__tablename__ = f"{self.__table_prefix__}__{self.__tablename__}"
        super().__init_subclass__()


class User(DeclarativeBase):
    __tablename__ = "users"

    user_id = Column(BIGINT(unsigned=False), primary_key=True, autoincrement=False)
    joined = Column(DateTime(timezone=True), default=func.now())
    last_active = Column(DateTime(timezone=True), default=func.now())

    def __repr__(self):
        return str(self.code)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
