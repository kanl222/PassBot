from typing import Dict
from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Table
from sqlalchemy.orm import relationship
from app.core.security import crypto
from ..db_session import SqlAlchemyBase
from enum import Enum as PyEnum


class UserRole(str, PyEnum):
    STUDENT = "student"
    TEACHER = "teacher"



class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(String(50), unique=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    _encrypted_data_user = Column(String(500), nullable=True)

    def set_encrypted_data(self, user_data: dict[str, str]) -> None:
        """
        Sets encrypted user data.

        :param user_data: Dictionary with user data (e.g., username and password).
        """
        try:
            encoded: bytes | None = crypto.encrypt(user_data)
            self._encrypted_data_user: bytes | None = encoded
        except Exception as e:
            raise ValueError(f"Data encryption error: {e}")

    def get_encrypted_data(self) -> dict:
        """
        Gets decrypted user data.

        :return: Dictionary with user data.
        """
        if not self._encrypted_data_user:
            raise ValueError("There is no encrypted data for this user.")
        try:
            decoded: Dict[str, Any] | None = crypto.decrypt(self._encrypted_data_user)
            return decoded
        except Exception as e:
            raise ValueError(f"Error decrypting data: {e}")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, full_name={self.full_name}, role={self.role})>"


class Student(User):
    __tablename__ = 'students'

    id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    kodstud = Column(Integer, nullable=True)
    id_stud = Column(Integer, nullable=True)
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=True)

    group = relationship("Group", back_populates="students", foreign_keys=[group_id])
    # absences = relationship("Absence", back_populates="student")

    def __repr__(self) -> str:
        return f"<Student(id={self.id}, full_name={self.full_name}, group_id={self.group_id})>"


class Teacher(User):
    __tablename__: str = 'teachers'

    id = Column(Integer, ForeignKey('users.id'), primary_key=True)

    def __repr__(self) -> str:
        return f"<Teacher(id={self.id}, full_name={self.full_name})>"

from .groups import Group
User.curated_groups = relationship("Group", back_populates="curator", foreign_keys=[Group.id_curator])
