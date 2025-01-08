import traceback
from typing import Dict, List, Any, Tuple
from async_lru import alru_cache
import asyncio
import logging

from sqlalchemy import  select
from sqlalchemy.ext.asyncio import AsyncSession
from app.bot.handlers import teacher
from app.db.crud.groups import get_or_create_group
from app.db.db_session import with_session
from app.parsers.urls import link_teacher_supervision, link_to_activity

from app.db.crud.users import get_teacher, get_user_of_telegram_id
from app.session.session_manager import SessionManager
from app.parsers.group_parser import GroupParser
from app.parsers.student_parser import StudentParser
from app.db.models.users import Student, Teacher, User, UserRole
from app.db.models.groups import Group

class TeacherDataUpdater:
    def __init__(self, auth_payload: Dict[str,str],id_telegram: int) -> None: 
        self.login: str = auth_payload['login']
        self.password: str = auth_payload['password']
        self.id_telegram: int = id_telegram

    @alru_cache(maxsize=1000)
    @with_session
    async def _get_existing_students(self, db_session: AsyncSession) -> Dict[str, Student]:  # Type hint corrected
        """Bulk fetch existing students."""
        result = await db_session.execute(select(Student).filter_by(group_id=None))
        return {user.full_name: user for user in result.scalars()}

    async def _update_group_students(
        self,
        sm: SessionManager,
        group: Dict,
        user: User,
        existing_students: Dict[str, Student],
    ) -> List[Student]:
        """Process students for a single group."""

        _group = await get_or_create_group(id_curator=user.id, _id_group=group["id"], name=group["name"])
        response = await sm.session.get(link_to_activity.format(id_group=group["id"]))
        students_data = await StudentParser.parse_students_list(await response.text())

        processed_students = []
        for student_data in students_data:
            if existing_student := existing_students.get(student_data["full_name"]):
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

        user = await get_user_of_telegram_id(telegram_id=self.id_telegram)
        if not user: raise ValueError("User not found.")

        existing_students = await self._get_existing_students(db_session=db_session)

        async with SessionManager(self.login, self.password) as sm:
            try:
                response = await sm.session.get(link_teacher_supervision)
                groups_data = GroupParser.parse_groups(await response.text()) 

                group_tasks = [
                    await self._update_group_students(sm, group, user, existing_students)
                    for group in groups_data
                ]
                results = await asyncio.gather(*group_tasks)

                all_students = []
                all_groups = []
                for students, _ in results:
                    all_students.extend(students)
 
                db_session.add_all(all_students)  
                await db_session.commit()

                return {"groups_count": len(groups_data), "students_count": len(all_students)}

            except Exception as e:
                logging.error(f"Error processing teacher data: {e}")
                await db_session.rollback()
                traceback.print_exc()
                raise
            
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
            raise

    @staticmethod
    async def _fetch_groups(id_telegram:int) -> List[Dict]:
        """Fetch groups for a teacher."""
        teacher: Teacher | List[Teacher] | None = await get_teacher(telegram_id=id_telegram)
        if teacher:
            return [{"id": group.id, "name": group.name} for group in teacher.curated_groups]
        return []

    @staticmethod
    async def _fetch_students(id_telegram:int) -> List[Dict]:
        """Fetch students for given groups."""
        teacher: Teacher | List[Teacher] | None = await get_teacher(telegram_id=id_telegram)
        if teacher:
            students = []
            for group in teacher.curated_groups:
                students.extend({"name": student.full_name} for student in group.students)
            return students

async def first_parser_data(telegram_id: int) -> Dict[str, int]:
    """
    Wrapper function for teacher data processing with improved performance.
    """
    try:
        teacher: Teacher = await get_teacher(telegram_id=telegram_id)
        processor =  TeacherDataUpdater(auth_payload=teacher.get_encrypted_data(),id_telegram=telegram_id)
        return await processor.update_teacher_data()
    except Exception as e:
        print(e)
    
