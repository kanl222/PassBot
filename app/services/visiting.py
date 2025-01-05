import datetime
import logging
import asyncio
from dataclasses import dataclass
from contextlib import asynccontextmanager
from typing import Any, Dict, Generator, List, Optional

from app.tools.support import timeit
from app.db.models.users import Teacher
from app.parsers.attendance_parser import AttendanceParser
from app.services.users import get_all_teacher
from app.session.session_manager import SessionManager
from app.parsers.urls import link_to_activity_is_time
from app.db.db_session import get_session


@dataclass
class AttendanceRecord:
    """Structured representation of attendance data."""

    teacher_id: int
    group_id: int
    student_id: int
    status: str
    date: datetime.datetime


@asynccontextmanager
async def teacher_session(teacher: Teacher) -> Generator[SessionManager, Any, None]: # type: ignore
    """Context manager for teacher session management."""
    login_password: Dict[str, Any] = teacher.get_encrypted_data()
    async with SessionManager(login_password["login"], login_password["password"]) as sm:
        yield sm


class _AttendanceParser:
    @classmethod
    async def parse_group_attendance(
        cls,
        sm: SessionManager,
        group,
        teacher: Teacher,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
    ) -> List[AttendanceRecord]:
        """Parse attendance for a single group within a date range."""

        url = link_to_activity_is_time.format(
            id_group=group._id_group,
            stdt=start_date.strftime("%d.%m.%Y"),
            endt=end_date.strftime("%d.%m.%Y"),
        )
        try:
            async with sm.session.get(url) as activities:  
                attendance_data: List[Dict[str, Any]] = await AttendanceParser.parse_attendance(
                    await activities.text()
                )
                if attendance_data:
                    return []
                return [
                    AttendanceRecord(
                        teacher_id=teacher.id, 
                        group_id=group.id,  
                        student_id=data.get("name"),
                        status=data.get("attendance"),
                        date=date,
                    )
                    for data in attendance_data
                    for date in date_range(start_date,end_date) 
                ]
        except Exception as e:
            logging.error(f"Error parsing group {group._id_group}: {e}")
            return []

    @classmethod
    async def parse_teacher_attendance(
        cls, teacher: Teacher, start_date: datetime.datetime, end_date: datetime.datetime
    ) -> List[AttendanceRecord]:
        """Parse attendance for all groups of a teacher within a date range."""

        async with teacher_session(teacher) as sm:
            group_tasks: List[asyncio.Coroutine[Any, Any, List[AttendanceRecord]]] = [
                cls.parse_group_attendance(sm, group, teacher, start_date, end_date)
                for group in teacher.curated_groups
            ]
            group_attendances: List[List[AttendanceRecord]] = await asyncio.gather(*group_tasks)
            return [
                record
                for group_attendance in group_attendances
                for record in group_attendance
            ]


def date_range(start_date, end_date) -> Generator[Any, Any, None]:
    """Generator for date range."""
    current_date = start_date
    while current_date <= end_date:
        yield current_date
        current_date += datetime.timedelta(days=1)

@timeit
async def pars_visiting(
    start_date: datetime.datetime = None, end_date: datetime.datetime = None  
) -> List[AttendanceRecord]:
    
    if start_date is None and end_date is None:
        start_date = datetime.date(2024,12,22)
        end_date = datetime.date(2024,12,25)
        # start_date = end_date = datetime.datetime.now()
    
    if start_date > end_date:
        raise ValueError("start_date must be less than or equal to end_date")
    
    teachers: List[List[Teacher] | None] = [await get_all_teacher()]
    all_attendances = []

    teacher_tasks: List[asyncio.Coroutine[Any, Any, List[AttendanceRecord]]] = [
        _AttendanceParser.parse_teacher_attendance(teacher, start_date, end_date)
        for teacher in teachers
    ]
    results =await asyncio.gather(*teacher_tasks)
    for result in results:
        all_attendances.extend(result)

    return all_attendances

