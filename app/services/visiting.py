import datetime
from functools import lru_cache
import logging
import asyncio
from dataclasses import dataclass
from contextlib import asynccontextmanager
import traceback
from typing import Any, Dict, Generator, List, Optional
from async_lru import alru_cache
import pandas as pd
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.handlers import student
from app.db.models.absences import Visiting
from app.db.models.groups import Group
from app.db.models.pairs import Pair
from app.db.crud.pairs import get_or_create_pair
from app.db.models.group_pair import group_pair_association
from app.tools.support import import_html_log, timeit
from app.db.models.users import Student, Teacher
from app.parsers.attendance_parser import AttendanceParser
from app.db.crud.users import get_all_teachers, get_student
from app.session.session_manager import SessionManager
from app.parsers.urls import link_to_activity_is_time
from app.db.db_session import get_session, with_session

@dataclass
class AttendanceRecord:
    teacher_id: int
    group_id: int
    student_id: int
    status: str
    date: datetime.datetime
    detail: str
    discipline: str
    pair_number: str


@asynccontextmanager
async def teacher_session(teacher: Teacher) -> Generator[SessionManager, Any, None]:  # type: ignore
    """Context manager for teacher session management."""
    login_password: Dict[str, Any] = teacher.get_encrypted_data()
    async with SessionManager(
        login_password["login"], login_password["password"]
    ) as sm:
        yield sm


class AttendanceParserService:
    @classmethod
    async def parse_group_attendance(
        cls,
        sm: SessionManager,
        group: Group,
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
            attendance_data: pd.DataFrame = await AttendanceParser.parse_attendance(
                html_content=import_html_log()
            )
            attendance_data_group = attendance_data.groupby('kodstud')
            attendance_records = []
            for student in group.students:
                if student.kodstud in attendance_data_group.groups:
                    student_attendance = attendance_data_group.get_group(student.kodstud)
                    attendance_records.extend(
                        AttendanceRecord(
                            teacher_id=teacher.id,
                            group_id=group.id,
                            student_id=student.id,
                            status=data["status"],
                            date=data["date"],
                            detail=data["details"],
                            discipline=data["discipline"],
                            pair_number=data["pair_number"],
                        )
                        for _, data in student_attendance.iterrows()
                    )
            return attendance_records
        except Exception as e:
            logging.error(f"Error parsing group {group._id_group}: {e}")
            return []

    @classmethod
    async def parse_teacher_attendance(
        cls,
        teacher: Teacher,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
    ) -> List[AttendanceRecord]:
        """Parse attendance for all groups of a teacher within a date range."""

  
        group_tasks: List[asyncio.Coroutine[Any, Any, List[AttendanceRecord]]] = [
                cls.parse_group_attendance( None,group, teacher, start_date, end_date)
                for group in teacher.curated_groups[:1]
            ]
        group_attendances: List[List[AttendanceRecord]] = await asyncio.gather(
                *group_tasks
            )
        return [
                record
                for group_attendance in group_attendances
                for record in group_attendance
            ]


@timeit
async def parse_visiting_of_pair(
    start_date: Optional[datetime.datetime] = None,
    end_date: Optional[datetime.datetime] = None,
) -> None:
    """Main function for parsing visiting records."""
    try:
        start_date = start_date or datetime.datetime.now()
        if end_date is None or end_date > datetime.datetime.now():
            end_date = datetime.datetime.now()

        if start_date > end_date:
            raise ValueError("start_date must be less than or equal to end_date")

        teachers: List[Teacher] = await get_all_teachers()
        teacher_tasks = [
            AttendanceParserService.parse_teacher_attendance(teacher, start_date, end_date)
            for teacher in teachers
        ]
        results = await asyncio.gather(*teacher_tasks)
        all_attendances = [record for result in results for record in result]
        await save_attendance_records(pd.DataFrame(all_attendances))
    except Exception as e: 
        traceback.print_exc()


@with_session
async def save_attendance_records(attendance_df: pd.DataFrame, db_session: AsyncSession):
    """Saves attendance records from a Pandas DataFrame to the database."""
    try:
        if attendance_df.empty:
            logging.warning("No attendance records to save.")
            return

        visiting_records = []
        pair_groups_map = {}

        for (date, discipline, pair_number), group_df in attendance_df.groupby(['date', 'discipline', 'pair_number']):
            pair = await get_or_create_pair(db_session=db_session, date=date, pair_number=pair_number, discipline=discipline)
            if not pair:
                logging.warning(f"Skipping pair for {date}, {discipline}, {pair_number}")
                continue

            group_ids = group_df['group_id'].unique()
            if pair.id not in pair_groups_map:
                groups = await get_groups_by_ids(db_session, group_ids)
                await associate_pair_with_groups(db_session, pair, groups)
                pair_groups_map[pair.id] = groups

            visiting_records.extend(
                Visiting(
                    student_id=record['student_id'],
                    pair_id=pair.id,
                    status=record['status'],
                    message=record['detail'],
                )
                for _, record in group_df.iterrows()
                if student
            )
        db_session.add_all(visiting_records)
        await db_session.commit()
        logging.info(f"Saved {len(visiting_records)} attendance records.")
    except Exception as e:
        traceback.print_exc()
        logging.error(f"Error saving attendance records: {e}")
        await db_session.rollback()

@lru_cache(100)
async def get_groups_by_ids(db_session: AsyncSession, group_ids: List[int]) -> List[Group]:
    """Retrieve groups by their IDs."""
    query = select(Group).filter(Group.id.in_(group_ids))
    result = await db_session.execute(query)
    return result.scalars().all()


async def associate_pair_with_groups(db_session: AsyncSession, pair: Pair, groups: List[Group]) -> None:
    """Associate a pair with multiple groups."""
    for group in groups:
        if pair not in group.pairs:
            insert_query = insert(group_pair_association).values(group_id=group.id, pair_id=pair.id)
            db_session.execute(insert_query)
    await db_session.commit()