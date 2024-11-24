from sqlalchemy import Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..db.db_session import SqlAlchemyBase


class UserRole(str, Enum):
	STUDENT = "student"
	TEACHER = "teacher"


class User(SqlAlchemyBase):
	__tablename__ = 'users'

	id = Column(Integer, primary_key=True, autoincrement=True)
	telegram_id = Column(String(50), unique=True, nullable=False)
	full_name = Column(String(255), nullable=False)
	role = Column(Enum(UserRole), nullable=False, default=UserRole.STUDENT)
	group_id = Column(Integer, ForeignKey('groups.id'), nullable=True)

	group = relationship('Group', back_populates='students')
	sent_messages = relationship('Message', back_populates='sender')
	absences = relationship('Absence', back_populates='student')
	telegram = relationship('User_Telegram',back_populates='users_telegram'														   '')
	def __repr__(self):
		return f"<User(name={self.full_name}, role={self.role})>"
