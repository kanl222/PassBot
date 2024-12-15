from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy import func
from ..db_session import SqlAlchemyBase
from enum import Enum as PyEnum


class AbsenceReason(str, PyEnum):
    SICKNESS = "sickness"
    PERSONAL = "personal"
    OTHER = "other"


class Absence(SqlAlchemyBase):
    __tablename__: str = 'absences'

    id = Column(Integer, primary_key=True, autoincrement=True)
    reason = Column(Enum(AbsenceReason), nullable=False)
    description = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    student = relationship('Student', back_populates='absences')

    def __repr__(self) -> str:
        return f"<Absence(student={self.student.full_name}, reason={self.reason}, timestamp={self.timestamp})>"
