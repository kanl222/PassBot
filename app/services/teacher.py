from collections import defaultdict
from datetime import date
import json
import traceback
from typing import Dict, List, Any, Optional, Tuple
from async_lru import alru_cache
import asyncio
import logging

from sqlalchemy import  distinct, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.crud.groups import create_group, get_group, get_or_create_group
from app.db.db_session import with_session
from app.db.models.absences import AttendanceStatus, Visiting
from app.db.models.pairs import Pair
from app.parsers.urls import link_teacher_supervision, link_to_activity

from app.db.crud.users import get_teacher, get_user_of_telegram_id
from app.session.session_manager import SessionManager, create_session, require_website_access
from app.parsers.group_parser import GroupParser
from app.parsers.student_parser import StudentParser
from app.db.models.users import Student, Teacher, User, UserRole
from app.db.models.groups import Group

class TeacherDataUpdater:
    def __init__(self,id_telegram: int) -> None: 
        
        self.id_telegram: int = id_telegram

    
    @with_session
    async def _get_existing_students(self, db_session: AsyncSession) -> Dict[str, Student]:  # Type hint corrected
        """Bulk fetch existing students."""
        result = await db_session.execute(select(Student))
        return {user.full_name: user for user in result.scalars()}

    async def _update_group_students(
        self,
        sm: SessionManager,
        group: Dict,
        user: User,
        existing_students: Dict[str, Student],
    ) -> List[Student]:
        """Process students for a single group."""
        _group = await get_or_create_group(
            id_curator=user.id, 
            _id_group=group["id"], 
            name=group["name"]
        )

        async with await sm.get(link_to_activity.format(id_group=group["id"])) as response:
            students_data = await StudentParser.parse_students_list(await response.text())

        processed_students = []
        for student_data in students_data:
            if existing_student := existing_students.get(
                student_data["full_name"]
            ):
                if existing_student.group_id is not None:
                    break
                student = existing_student
                student.group_id = _group.id
            else:
                student = Student(
                        id_stud=student_data["id_stud"],
                        kodstud=student_data["kodstud"],
                        full_name=student_data["full_name"],
                        role=UserRole.STUDENT,
                        group_id=_group.id,
                )
                existing_students[student.full_name] = student
            processed_students.append(student)

        return processed_students, _group 

    @with_session
    async def update_teacher_data(self, db_session: AsyncSession) -> Dict[str, int]:
        """Efficiently process and store teacher's group and student data."""

        user = await get_teacher(telegram_id=self.id_telegram)
        if not user:
            raise ValueError("User not found.")

        existing_students = await self._get_existing_students(db_session=db_session)

        async with create_session(user) as sm:
                async with await sm.get(link_teacher_supervision) as response:
                    groups_data = await GroupParser.parse_groups(await response.text())

                group_tasks = []
                for group in groups_data:  
                    task = self._update_group_students(sm, group, user, existing_students)
                    group_tasks.append(task)
                results = await asyncio.gather(*group_tasks)  
                all_students = []
                for students, group_obj in results: 
                        all_students.extend(students)
                        await db_session.merge(group_obj)
                        
                if not user.is_data_parsed:
                    user.is_data_parsed = True
                    await db_session.merge(user)
                    
                db_session.add_all(all_students)
                await db_session.commit()

                return {"groups_count": len(groups_data), "students_count": len(all_students)}



            
class TeacherDataService:
            
    @classmethod
    async def parse_and_update_teacher_data(cls,telegram_id:int) -> None:
        """
        Orchestrate the parsing of teacher-related data with progress tracking.

        Args:
            auth_data: Authentication data for the teacher.
        """

        try:
            await first_parser_data(telegram_id=telegram_id)
        except Exception as e:
            logging.error(f"Data parsing error: {e}")
            raise e

    @staticmethod
    async def fetch_groups(id_telegram:int)  -> list[dict[str, Any]] | list:
        """Fetch groups for a teacher."""
        teacher: Teacher | List[Teacher] | None = await get_teacher(telegram_id=id_telegram)
        if teacher:
            return [{"id": group.id, "name": group.name} for group in teacher.curated_groups]
        return []

    @staticmethod
    async def fetch_students(teacher_id: int) -> Dict[str, List[Student]]:
        """Fetch students curated by a teacher, grouped by group name."""
        teacher = await get_teacher(telegram_id=teacher_id)
        if teacher:
            return {group.name: group.students for group in teacher.curated_groups}
        return {}
    
    
    @staticmethod
    @with_session
    async def fetch_student_absences(
        teacher_id: int,
        start_date: date,
        end_date: date,
        db_session: AsyncSession,
    ) -> Dict[str, Dict[str, List[str]]]:
        """Fetch student absences within a date range, grouped by group and student."""

        teacher: Optional[Teacher] = await get_teacher(telegram_id=teacher_id)
        if not teacher:
            return {}

        absences: Dict[str, Dict[str, List[str]]] = {}
        for group in teacher.curated_groups:
            absences[group.name] = {'group': group, 'data': defaultdict(lambda: {'dates': [], 'name': ''})}

            query = (
                select(Pair.date, Student.id, Student.full_name)
                .select_from(Visiting)
                .join(Pair)
                .join(Student)
                .filter(
                    Student.group_id == group.id,
                    Pair.date.between(start_date, end_date),
                    Visiting.status != AttendanceStatus.PRESENT,
                )
            )

            result = await db_session.execute(query)
            for pair_date, student_id, student_name in result:
                absences[group.name]['data'][student_id]['dates'].append(pair_date)
                absences[group.name]['data'][student_id]['name'] = student_name
        return absences

@require_website_access
async def first_parser_data(telegram_id: int)  -> Any | None:
    
    """
    Wrapper function for teacher data processing with improved performance.
    """
    processor =  TeacherDataUpdater(id_telegram=telegram_id)
    return await processor.update_teacher_data()

    
