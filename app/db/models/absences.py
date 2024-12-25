import datetime
from enum import Enum, auto
from typing import Optional
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base
from ..db_session import SqlAlchemyBase


class AttendanceStatus(Enum):
    PRESENT = auto()
    ABSENT = auto()
    LATE = auto()
    EXCUSED = auto()
    NOT_CONFIRMED = auto()

class Visiting(SqlAlchemyBase):
    __tablename__ = 'visiting'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey('students.id', ondelete='CASCADE'), 
        nullable=False, 
        index=True
    )

    date: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.datetime.utcnow, 
        nullable=False, 
        index=True
    )
    status: Mapped[AttendanceStatus] = mapped_column(
        nullable=False
    )
    message: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
        )

    student = relationship("Student", back_populates="visits")



    __table_args__ = (
        Index('idx_student_date', student_id, date),
    )

    def __repr__(self) -> str:
        return (
            f"<Visiting("
            f"student_id={self.student_id}, "
            f"status={self.status}, "
            f"date={self.date})>"
        )
