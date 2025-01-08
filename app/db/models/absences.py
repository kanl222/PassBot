import datetime
from enum import Enum, auto
from typing import Optional
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column
from ..db_session import SqlAlchemyBase


class AttendanceStatus(Enum):
    PRESENT = auto()
    ABSENT = auto()
    LATE = auto()
    EXCUSED = auto()
    NOT_CONFIRMED = auto()


class Visiting(SqlAlchemyBase):
    __tablename__ = "visiting"

    id: Mapped[int] = mapped_column(
        __name_pos=Integer, primary_key=True, autoincrement=True
    )
    student_id: Mapped[int] = mapped_column(
        __name_pos=Integer,
        __type_pos=ForeignKey(column="students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    pair_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(column="pairs.id"),
        nullable=False,
        index=True,
    )
    status: Mapped[AttendanceStatus] = mapped_column(nullable=False)

    message: Mapped[Optional[str]] = mapped_column(
        __name_pos=String(length=255), nullable=True
    )

    student: Mapped["Student"] = relationship(
        argument="Student", back_populates="visits"
    )
    pair: Mapped["Pair"] = relationship(argument="Pair", back_populates="visits")

    __table_args__: tuple[Index] = (
        Index("idx_student_pair", "student_id", "pair_id", unique=True),
    )

    def __repr__(self) -> str:
        return f"<Visiting(student_id={self.student_id}, pair_id={self.pair_id}, status={self.status})>"
