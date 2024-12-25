from ast import List
from typing import Dict, Any, Optional
from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship, Mapped, mapped_column, declarative_base
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm.properties import MappedColumn
from app.core.security import crypto
from enum import Enum as PyEnum, auto
from ..db_session import SqlAlchemyBase


class UserRole(PyEnum):
    STUDENT = auto()
    TEACHER = auto()


class User(SqlAlchemyBase):
    """Base user model with efficient encryption methods."""
    __tablename__: str = 'users'

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    full_name: MappedColumn[str] = mapped_column(
        String(255),
        nullable=False
    )

    telegram_id: MappedColumn[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )

    _encrypted_data_user: MappedColumn[str] = mapped_column(
        String(500),
        nullable=True
    )

    role: MappedColumn[UserRole] = mapped_column(
        Enum(UserRole),
        nullable=False
    )

    def set_encrypted_data(self, user_data: Dict[str, str]) -> None:
        try:
            self._encrypted_data_user = crypto.encrypt(user_data)
        except Exception as e:
            raise ValueError(f"Data encryption error: {e}")

    def get_encrypted_data(self) -> Dict[str, Any]:
        if not self._encrypted_data_user:
            raise ValueError("No encrypted data available.")

        try:
            return crypto.decrypt(self._encrypted_data_user)
        except Exception as e:
            raise ValueError(f"Decryption error: {e}")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, full_name={self.full_name}, role={self.role})>"

from .groups import Group

class Student(User):
    """Student-specific user model with optimized relationships."""
    __tablename__ = 'students'

    id: Mapped[int] = mapped_column(
        ForeignKey('users.id'),
        primary_key=True
    )

    kodstud: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )

    id_stud: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )

    group_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('groups.id'),
        nullable=True,
        index=True
    )

    group = relationship(
        Group, 
        back_populates="students", 
        foreign_keys=[group_id],
        lazy='selectin'
    )
    
    visits = relationship(
        "Visiting", 
        back_populates="student",
        foreign_keys="[Visiting.student_id]",
        lazy='selectin'
    )



    __mapper_args__: Dict[str, UserRole] = {
        "polymorphic_identity": UserRole.STUDENT
    }

    def __repr__(self) -> str:
        return f"<Student(id={self.id}, full_name={self.full_name}, group_id={self.group_id})>"


class Teacher(User):
    """Teacher-specific user model with efficient group relationships."""
    __tablename__: str = 'teachers'

    id: Mapped[int] = mapped_column(
        ForeignKey('users.id'),
        primary_key=True
    )

    curated_groups = relationship(
        Group,
        back_populates="curator",
        lazy='selectin'
    )

    __mapper_args__: Dict[str, UserRole] = {
        "polymorphic_identity": UserRole.TEACHER
    }

    def __repr__(self) -> str:
        return f"<Teacher(id={self.id}, full_name={self.full_name})>"
