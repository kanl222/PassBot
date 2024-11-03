from optparse import Option

from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy import func
from pydantic import BaseModel
from datetime import datetime

from ..db.db_session import SqlAlchemyBase


class AbsenceReason(str, Enum):
    SICKNESS = "sickness"
    PERSONAL = "personal"
    OTHER = "other"


class Absence(BaseModel):
    id: int
    reason: AbsenceReason
    description: str
    timestamp: datetime


class Absence(SqlAlchemyBase):
    __tablename__ = 'absences'

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    reason: AbsenceReason = Column(Enum(AbsenceReason), nullable=False)
    description: str = Column(Text, nullable=True)
    timestamp: datetime = Column(DateTime(timezone=True), server_default=func.now())

    student_id: int = Column(Integer, ForeignKey('users.id'), nullable=False)
    student = relationship('User', back_populates='absences')

    def __repr__(self):
        return f"<Absence(student={self.student.full_name}, reason={self.reason}, timestamp={self.timestamp})>"
