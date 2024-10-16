import datetime
from enum import unique

from pydantic import BaseModel
from sqlalchemy import Column, Integer, ForeignKey, String, Boolean,DateTime
from pydantic import constr, validator
from ..db.db_session import SqlAlchemyBase
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import func
from sqlalchemy_serializer import SerializerMixin


class User(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    first_name = Column(String, nullable=False, unique=False,)
    sec_name = Column(String, nullable=False, unique=False,)
    osu_uid_username = Column(String, nullable=True,unique=True,index=True)
    telegram_id_user = Column(String,nullable=True)
    type_user = Column(String)
    created_at = Column(DateTime, nullable=False, default=func.now)

    __serialize_only__ = ('id', 'first_name', 'sec_name', 'osu_uid_username','telegram_id_user')


    def to_dict(self):
        return {attr: getattr(self, attr) for attr in self.__serialize_only__}

    def __repr__(self):
        return f"User({self.to_dict()})"
