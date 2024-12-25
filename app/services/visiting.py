import datetime
import logging
import asyncio
from dataclasses import dataclass
from contextlib import asynccontextmanager
from typing import List, Optional

from app.db.models.users import Teacher
from app.parsers.attendance_parser import VisitingParser
from app.services.users import get_all_teachers
from app.session.session_manager import SessionManager
from app.parsers.urls import link_to_activity_is_time
from app.db.models.absences import Absence
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
async def teacher_session(teacher: Teacher):
    """
    Context manager for teacher session management.
    
    Args:
        teacher: Teacher instance
    
    Yields:
        Authenticated session manager
    """
    login_password = teacher.get_encrypted_data()
    async with SessionManager(login_password['login'], login_password['password']) as sm:
        yield sm

class AttendanceParser:
    @classmethod
    async def parse_group_attendance(
        cls, 
        sm: SessionManager, 
        group, 
        teacher: Teacher, 
        date: datetime.datetime
    ) -> List[AttendanceRecord]:
        """
        Parse attendance for a single group.
        
        Args:
            sm: Session manager
            group: Group to parse
            teacher: Teacher of the group
            date: Date for attendance parsing
        
        Returns:
            List of attendance records
        """
        url = link_to_activity_is_time.format(
            id_group=group._id_group, stdt=date, end_date=date)

        try:
            async with await sm.get(url) as activities:
                attendance_data = await VisitingParser.parse_attendance(await activities.text())
                return [
                    AttendanceRecord(
                        student_id=data.get("student_id"),
                        status=data.get("status"),
                        date=date
                    )
                    for data in attendance_data
                ]
        except Exception as e:
            logging.error(f"Error parsing group {group._id_group}: {e}")
            return []

    @classmethod
    async def parse_teacher_attendance(
        cls, 
        teacher: Teacher, 
        date: datetime.datetime
    ) -> List[AttendanceRecord]:
        """
        Parse attendance for all groups of a teacher.
        
        Args:
            teacher: Teacher to parse attendance for
            date: Date for attendance parsing
        
        Returns:
            List of attendance records
        """
        async with teacher_session(teacher) as sm:
            group_tasks = [
                cls.parse_group_attendance(sm, group, teacher, date)
                for group in teacher._curated_groups
            ]
            
            group_attendances = await asyncio.gather(*group_tasks)
            return [
                record 
                for group_attendance in group_attendances 
                for record in group_attendance
            ]

async def pars_visiting(
    start_date: Optional[datetime.datetime] = None, 
    end_date: Optional[datetime.datetime] = None
) -> None:
    """
    Parse attendance for all teachers.
    
    Args:
        start_date: Start date for attendance parsing
        end_date: End date for attendance parsing
    """
    date = start_date or end_date or datetime.datetime.now()
    teachers = await get_all_teachers()

    all_attendances = []
    for teacher in teachers:
        try:
            teacher_attendances = await AttendanceParser.parse_teacher_attendance(teacher, date)
            all_attendances.extend(teacher_attendances)
        except Exception as e:
            logging.error(f"Error processing teacher {teacher.full_name}: {e}")

    await bulk_save_attendances(all_attendances)

async def bulk_save_attendances(attendances: List[AttendanceRecord]) -> None:
    """
    Save attendance records in bulk.
    
    Args:
        attendances: List of attendance records to save
    """
    if not attendances:
        return

    try:
        async with get_session() as db_session:
            db_session.add_all(attendances)
            await db_session.commit()
    except Exception as e:
        logging.error(f"Bulk attendance save error: {e}")
