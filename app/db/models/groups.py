from typing import List
from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import relationship, Mapped, mapped_column, declarative_base
from sqlalchemy.ext.declarative import declared_attr
from ..db_session import SqlAlchemyBase


class Group(SqlAlchemyBase):
    __tablename__: str = 'groups'

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    id_curator: Mapped[int] = mapped_column(
        ForeignKey('users.id'),
        nullable=False,
        index=True
    )

    _id_group: Mapped[int] = mapped_column(
        unique=True,
        nullable=False,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )
    curator: Mapped["Teacher"] = relationship(
        "Teacher",
        back_populates="curated_groups",
        foreign_keys=[id_curator],
        lazy='selectin',
        cascade='save-update'
    )

    students: Mapped[List["Student"]] = relationship(
        "Student",
        back_populates="group",
        foreign_keys="Student.group_id",
        lazy='selectin',
        cascade='save-update'
    )

    __table_args__ = (
        Index('idx_curator_group', id_curator, _id_group),
    )

    def __repr__(self) -> str:
        return f"<Group(name={self.name}, id={self.id})>"
