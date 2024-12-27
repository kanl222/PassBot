from typing import Dict, List, Any, Tuple
from functools import lru_cache
import asyncio
import logging

from aiohttp import ClientResponse
from sqlalchemy import Result, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.bot.handlers import teacher
from app.db.db_session import with_session
from app.parsers.urls import link_teacher_supervision, link_to_activity
from app.services import auth
from app.services.users import get_teacher, get_user_instance
from app.session.session_manager import SessionManager
from app.parsers.group_parser import GroupParser
from app.parsers.student_parser import StudentParser
from app.db.models.users import Student, User, UserRole
from app.db.models.groups import Group

class TeacherDataProcessor:
    def __init__(self, auth_payloud: Dict[str,str],id_telegram) -> None: 
        self.login = auth_payloud['login']
        self.password = auth_payloud['password']
        self.id_telegram = id_telegram

    @lru_cache(maxsize=1000)
    async def _get_existing_students(self, db_session: AsyncSession) -> Dict[str, User]:
        """
        Bulk fetch existing students to reduce database queries.
        
        Args:
            db_session: Database session for querying.
        
        Returns:
            Dictionary of students keyed by full name.
        """
        result = await db_session.execute(
            select(Student)
            .filter_by(Student.group_id is None)
        )
        return {user.full_name: user for user in result.scalars()}

    async def _process_group_students(
        self, 
        sm, 
        group: Dict, 
        user: User, 
        db_session: AsyncSession, 
        existing_students: Dict[str, User]
    ) -> List[Student]:
        """
        Process students for a single group with optimized database operations.
        
        Args:
            sm: Session manager
            group: Group data
            user: Teacher user instance
            db_session: Database session
            existing_students: Cached existing students
        
        Returns:
            List of processed student instances
        """
        _group = Group(
            id_curator=user.id,
            id_group=group['id'],
            name=group['name']
        )
        db_session.add(_group)
        response:ClientResponse | None = await sm.get(link_to_activity.format(group=group['id_group']))
        students_data: List[Dict[str, Any]] = await StudentParser.parse_students_list( await response.text()
        )

        processed_students = []
        for student_data in students_data:
            if existing_student := existing_students.get(
                student_data["full_name"]
            ):
                student = Student(
                    id=existing_student.id,
                    id_stud=student_data["id_stud"],
                    kodstud=student_data["kodstud"],
                    group_id=_group.id
                )
            else:
                student = Student(
                    id_stud=student_data["id_stud"],
                    kodstud=student_data["kodstud"],
                    full_name=student_data["full_name"],
                    role=student_data["role"],
                    group_id=_group.id
                )

            db_session.add(student)
            processed_students.append(student)

        return processed_students

    @with_session
    async def process_teacher_data(self, db_session: AsyncSession) -> Dict[str, int]:
        """
        Efficiently process and store teacher's group and student data.
        """
        user: User | None = await get_user_instance(telegram_id=self.id_telegram)
        if not user or user.role != UserRole.TEACHER:
            raise ValueError("User is not a teacher or does not exist.")

        existing_students: Dict[str, User] = await self._get_existing_students(db_session)

        async with SessionManager(self.login, self.password) as sm:
            try:
                response: ClientResponse | None = await sm.get(link_teacher_supervision)
                groups = await GroupParser.parse_groups(await response.text())

                group_processing_tasks: List[asyncio.Coroutine[Any, Any, List[Student]]] = [
                    self._process_group_students(sm, group, user, db_session, existing_students)
                    for group in groups
                ]
                
                all_students = await asyncio.gather(*group_processing_tasks)
                all_students = [student for group_students in all_students for student in group_students]

                await db_session.commit()

                return {
                    "groups_count": len(groups),
                    "students_count": len(all_students),
                }

            except Exception as e:
                logging.error(f"Error processing teacher data: {e}")
                await db_session.rollback()
                raise

async def first_parser_data(telegram_id) -> Dict[str, int]:
    """
    Wrapper function for teacher data processing with improved performance.
    """
    print(telegram_id)
    auth_payloud = await get_teacher(telegram_id=telegram_id)
    print(auth_payloud)
    processor =  TeacherDataProcessor(auth_payloud=auth_payloud.get_encrypted_data(),id_telegram=telegram_id)
    logging.info(auth_payloud)
    return await processor.process_teacher_data()
