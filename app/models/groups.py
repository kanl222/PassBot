from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from ..db.db_session import SqlAlchemyBase


class Group(SqlAlchemyBase):
	__tablename__ = 'groups'

	id = Column(Integer, primary_key=True, autoincrement=True)
	_id_group = Column(Integer,unique=True,nullable=False)
	name = Column(String(100), unique=True, nullable=False)
	students = relationship('User', back_populates='group')

	def __repr__(self):
		return f"<Group(name={self.name})>"
