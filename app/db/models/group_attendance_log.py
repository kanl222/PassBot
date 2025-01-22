import datetime

from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..db_session import SqlAlchemyBase


class GroupAttendanceLog(SqlAlchemyBase):
    __tablename__: str = "group_attendance_logs"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False, index=True)
    last_parsed_at = Column(DateTime)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    group = relationship(
        "Group",
        back_populates="attendance_logs"
        )

