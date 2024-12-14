from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Table
from sqlalchemy.orm import relationship

from ..db_session import SqlAlchemyBase


class Group(SqlAlchemyBase):
    __tablename__: str = 'groups'

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_curator = Column(Integer, ForeignKey('users.id'), nullable=False)
    _id_group = Column(Integer, unique=True, nullable=False)
    name = Column(String(100), unique=True, nullable=False)
    students = relationship('User', back_populates='group')

    student = relationship('User', back_populates='groups')

    def __repr__(self) -> str:
        return f"<Group(name={self.name})>"
