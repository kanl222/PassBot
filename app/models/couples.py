import datetime
from pydantic import BaseModel
from sqlalchemy import Column, Integer, ForeignKey, String, Boolean,DateTime
from pydantic import constr, validator
from ..db.db_session import SqlAlchemyBase
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy_serializer import SerializerMixin


class Couple(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'couples'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    tittle = Column(String, nullable=True, unique=True, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.now)
    __serialize_only__ = ('id', 'title', 'icon', 'admin_chat')


    def to_dict(self):
        return {attr: getattr(self, attr) for attr in self.__serialize_only__}

    def __repr__(self):
        return f"Chat(id={self.id}, title='{self.title}')"
