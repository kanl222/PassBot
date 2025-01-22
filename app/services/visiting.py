import asyncio
import datetime
import logging
import time
import traceback
from collections import defaultdict
from dataclasses import dataclass
from functools import lru_cache, wraps
from typing import Any, Dict, Generator, List, Optional, Tuple

import pandas as pd
from sqlalchemy import Select, and_, desc, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from async_lru import alru_cache
from sqlalchemy.orm import joinedload
from app.db.crud.pairs import get_or_create_pair
from app.db.crud.users import get_all_teachers, get_teacher
from app.db.db_session import with_session
from app.db.models.absences import AttendanceStatus, Visiting, status_enum
from app.db.models.group_attendance_log import GroupAttendanceLog
from app.db.models.group_pair import group_pair_association
from app.db.models.groups import Group
from app.db.models.pairs import Pair
from app.db.models.users import Teacher
from app.core.settings import tz
from app.parsers.attendance_parser import AttendanceParser
from app.parsers.urls import link_to_activity_is_time
from app.session.session_manager import SessionManager, create_session, require_website_access
from app.tools.support import timeit

logger = logging.getLogger(__name__)


def control_parsing_group(func):

    @wraps(func)
    @with_session
    async def wrapper(*args, db_session: AsyncSession, **kwargs):
        group_id = kwargs['group'].id
        start_date = kwargs['start_date']
        end_date = kwargs['end_date']
        current_time = datetime.datetime.now(tz)

        log_entry_query = select(GroupAttendanceLog).filter_by(
            group_id=group_id).order_by(desc(GroupAttendanceLog.last_parsed_at))
        log_entry = (await db_session.execute(log_entry_query)).scalar_one_or_none()

        if log_entry:
            log_start_date = log_entry.start_date.date(
            ) if log_entry.start_date else None
            log_end_date = log_entry.end_date.date(
            ) if log_entry.end_date else None

            if log_end_date and log_end_date > start_date and log_start_date < start_date:
                kwargs['start_date'] = log_end_date
                logger.info(f"Adjusted start_date for group {group_id} to {kwargs['start_date']}.")

        if end_date > current_time.date():
            kwargs['end_date'] = current_time.date()
            end_date_for_log = current_time.date()
        else:
            end_date_for_log = end_date

        log_entry_data = {"last_parsed_at": current_time, "end_date": end_date_for_log}
        if log_entry:
            update_query = update(GroupAttendanceLog).where(
                GroupAttendanceLog.id == log_entry.id).values(log_entry_data)
            await db_session.execute(update_query)
        else:
            log_entry_data['start_date'] = start_date
            db_session.add(GroupAttendanceLog(
                group_id=group_id, **log_entry_data))

        try:
            result = await func(*args, **kwargs)
            await db_session.commit()
            return result
        except Exception as e:
            logger.error(f"Error during parsing: {e}", exc_info=True)
            await db_session.rollback()
            raise

    return wrapper


@dataclass
class AttendanceRecord:
    teacher_id: int
    group_id: int
    student_id: int
    status: str
    key_pair:int
    date: datetime.datetime
    detail: str
    discipline: str
    pair_number: str


class AttendanceParserService:

    @classmethod
    @control_parsing_group
    @timeit
    async def parse_group_attendance(
        cls, sm: SessionManager, group: Group, teacher: Teacher, start_date: datetime.datetime, end_date: datetime.datetime
    ) -> List[AttendanceRecord]:
        """Parse attendance for a group within a date range."""
        url = link_to_activity_is_time.format(
            id_group=group._id_group,
            stdt=start_date.strftime("%d.%m.%Y"),
            endt=end_date.strftime("%d.%m.%Y"),
        )
        try:
            async with await sm.get(url) as response:
                attendance_data = AttendanceParser.parse_attendance(await response.text())
            if attendance_data.empty:
                return []

            return cls._build_attendance_records(group, teacher, attendance_data)
        except Exception as e:
            logger.error(f"Error parsing group {group._id_group}: {e}",exc_info=True)
            return []

    @staticmethod
    def _build_attendance_records(group: Group, teacher: Teacher, attendance_data: pd.DataFrame) -> List[AttendanceRecord]:
        """Build AttendanceRecord objects from parsed data."""
        records = []
        attendance_data_grouped = attendance_data.groupby("kodstud")
        for student in group.students:
            if student.kodstud in attendance_data_grouped.groups:
                student_data = attendance_data_grouped.get_group(
                    student.kodstud)
                records.extend(
                    AttendanceRecord(
                        teacher_id=teacher.id,
                        group_id=group.id,
                        student_id=student.id,
                        key_pair=row["key_pair"],
                        status=row["status"],
                        date=row["date"],
                        detail=row["details"],
                        discipline=row["discipline"],
                        pair_number=row["pair_number"],
                    )
                    for _, row in student_data.iterrows()
                )
        return records

    @classmethod
    async def parse_teacher_attendance(
        cls, teacher: Teacher, start_date: datetime.date, end_date: datetime.date
    ) -> List[AttendanceRecord]:
        """Parse attendance for all groups of a teacher."""
        async with create_session(teacher) as sm:
            tasks = [
                cls.parse_group_attendance(
                    sm=sm, group=group, teacher=teacher, start_date=start_date, end_date=end_date)
                for group in teacher.curated_groups
            ]
            results = await asyncio.gather(*tasks)

        return [record for group_result in results for record in group_result]


@require_website_access
async def parse_visiting_of_pair(
    teacher_telegram_id: Optional[int] = None, start_date: Optional[datetime.date] = None, end_date: Optional[datetime.date] = None ) -> None:
    """Parse visiting records for a specific teacher or all teachers."""
    start_date = start_date or datetime.date(2025, 1, 1)
    end_date = end_date or datetime.date.today()

    if start_date > end_date:
        raise ValueError("start_date must be less than or equal to end_date")

    teachers = [await get_teacher(telegram_id=teacher_telegram_id)] if teacher_telegram_id else await get_all_teachers()

    if not teachers:
        logger.warning("No teachers found for parsing.")
        return

    tasks = [AttendanceParserService.parse_teacher_attendance(
        teacher, start_date, end_date) for teacher in teachers]
    results = await asyncio.gather(*tasks)
    if all_records := [record for result in results for record in result]:
        logger.info(f"Saving {len(all_records)} attendance records.")
        await save_attendance_records(attendance_df=pd.DataFrame(all_records),start_date=start_date, end_date=end_date)
    else:
        logger.info("No attendance records found.")


@with_session
@timeit
async def save_attendance_records(attendance_df: pd.DataFrame, db_session: AsyncSession,start_date: Optional[datetime.date], end_date: Optional[datetime.date] ):
    """
    Saves attendance records from a Pandas DataFrame to the database.
    """
    if attendance_df.empty:
        logging.warning("No attendance records to save.")
        return
    pairs_query = select(Pair).options(joinedload(Pair.visits)).filter(Pair.date.between(start_date, end_date))
    groups = {group.id: group for group in (await db_session.execute(select(Group))).scalars().unique()}
    pairs = {pair.key_pair: pair for pair in (await db_session.execute(pairs_query)).scalars().unique()}


    visiting_records = []
    pair_groups_map = []
    grouped_records = attendance_df.groupby(['key_pair','date', 'discipline', 'pair_number'])

    for (key_pair,date,discipline,pair_number), group_df in grouped_records:
        key_pair = int(key_pair)
        new_records_df = group_df
        if pair := pairs.get(key_pair):
            if pair.visits:
                existing_records = list(map(lambda visit: visit.student_id,pair.visits))
        
                new_records_df: pd.DataFrame = group_df[~group_df["student_id"].isin(existing_records)]
        else:
            pair = await get_or_create_pair(
            db_session=db_session,
            key_pair=key_pair,
            date=date,
            pair_number=pair_number,
            discipline=discipline
            )
        if not pair:
            logging.warning(f"Skipping pair: {date}, {discipline}, {pair_number}")
            continue
        group_ids = tuple(map(int, group_df['group_id'].unique()))
        if pair.id not in pair_groups_map:
            _groups = list(map(lambda _group: groups[_group],group_ids))
            await associate_pair_with_groups(db_session, pair,_groups)
            pair_groups_map.append(pair.id)
        
            

        if not new_records_df.empty:
                new_visiting_records = new_records_df.assign(
                    pair_id=pair.id,
                    status=new_records_df["status"].apply(status_enum),
                ).rename(columns={
                        "detail": "message"}).loc[
                    :, ["student_id", "pair_id", "status", "message"]
                ]
                visiting_records.extend(new_visiting_records.to_dict(orient="records"))
    if visiting_records:
        start = time.perf_counter_ns()
        await db_session.execute(insert(Visiting), visiting_records)
        await db_session.commit()
        end = time.perf_counter_ns()
        logging.info(f"Saved {len(visiting_records)} new attendance records.")
    else:
        logging.info("No new attendance records to save.")


async def associate_pair_with_groups(db_session: AsyncSession, pair: Pair, groups: List[Group]) -> None:
    """Associate a pair with multiple groups."""
    if values := [
        {'group_id': group.id, 'pair_id': pair.id}
        for group in groups
        if pair not in group.pairs
    ]:
        await db_session.execute(insert(group_pair_association), values)
