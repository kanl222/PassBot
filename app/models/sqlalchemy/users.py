from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.db_session import SqlAlchemyBase
from enum import Enum as PyEnum


class UserRole(str, PyEnum):
    STUDENT = "student"
    TEACHER = "teacher"


class User(SqlAlchemyBase):
	__tablename__ = 'users'

	id = Column(Integer, primary_key=True, autoincrement=True)
	telegram_id = Column(String(50), unique=True, nullable=False)
	full_name = Column(String(255), nullable=False)
	_kodstud = Column(Integer, nullable=True)
	user_id = Column(Integer, nullable=True)
	role = Column(Enum(UserRole), nullable=False, default=UserRole.STUDENT)
	group_id = Column(Integer, ForeignKey('groups.id'), nullable=True)
	_encrypted_data_user= Column(String(500), nullable=True)

	# Relationships
	group = relationship('Group', back_populates='students')
	sent_messages = relationship('Message', back_populates='sender')
	absences = relationship('Absence', back_populates='student')
