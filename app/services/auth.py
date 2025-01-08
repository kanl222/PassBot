import logging
from typing import Dict, Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import crypto
from app.db.crud.users import get_student
from app.db.db_session import with_session
from app.db.models.users import Student, UserRole, Teacher
from app.parsers.student_parser import StudentParser 
from app.parsers.teacher_parser import TeacherParser
from app.parsers.urls import link_to_login
from app.session.session_manager import SessionManager, is_teacher


class ServiceAuth:
    @staticmethod
    def create_response(status: str, **kwargs) -> Dict[str, Any]:
        """Create a standardized response dictionary."""
        return {"status": status, **kwargs}

    @staticmethod
    async def _register_teacher(
        session_manager: SessionManager,
        user_data: Dict[str, Any],
        login: str,
        password: str,
        telegram_id: int,
        db_session: AsyncSession, # type: ignore
    ) -> Dict[str, Any]:
        """Registers a teacher after successful authentication."""

        response = await session_manager.session.get(link_to_login)
        teacher_data = await TeacherParser.parse_teacher(await response.text())
        user_data |= teacher_data

        teacher = Teacher(
            full_name=user_data["full_name"],
            telegram_id=telegram_id,
            _encrypted_data_user=crypto.encrypt({"login": login, "password": password}),
            role=UserRole.TEACHER,
        )

        db_session.add(teacher)
        await db_session.commit()
        return ServiceAuth.create_response(
            "success", role=user_data["role"].value, user=user_data["full_name"]
        )

    @staticmethod
    async def _register_student(
        session_manager: SessionManager,
        user_data: Dict[str, Any],
        telegram_id: int,
        db_session: AsyncSession,
    ) -> Dict[str, Any]:
        """Registers or updates a student after successful authentication."""

        response = await session_manager.session.get(LOGIN_URL)
        student_data = await StudentParser.parse_student(await response.text())
        user_data |= student_data
        user_data["role"] = UserRole.STUDENT

        existing_student = await get_student(db_session, full_name=user_data["full_name"])

        if existing_student:
            existing_student.telegram_id = telegram_id
            await db_session.commit()
            return ServiceAuth.create_response(  
                "updated",
                role=existing_student.role.value,
                user=existing_student.full_name,
            )

        new_student = Student(
            full_name=student_data["full_name"],
            role=UserRole.STUDENT,
            telegram_id=telegram_id,
        )
        db_session.add(new_student)
        await db_session.commit()

        return ServiceAuth.create_response(
            "no_group", message="The teacher has not registered a group for this student."
        )

    @staticmethod
    @with_session
    async def authenticate_user(cls, 
        user_input_data: dict, db_session: AsyncSession
    ) -> dict:
        """Authenticates user credentials and registers/updates the user in the database."""

        login, password, telegram_id = (
            user_input_data["login"],
            user_input_data["password"],
            user_input_data["id_user_telegram"],
        )

        try:
            async with SessionManager(login, password) as session_manager:
                if not session_manager or not session_manager.status:
                    return cls.create_response(  # Use class method
                        "error",
                        message="Authentication failed",
                        details="Invalid login or password",
                    )
                user_data: Dict[str, Any] = {}
                is_user_teacher = await is_teacher(session_manager.session)  # Store result to avoid calling twice

                if is_user_teacher:  
                    return await cls._register_teacher(  
                        session_manager, user_data, login, password, telegram_id, db_session
                    )

                return await cls._register_student( 
                    session_manager, user_data, telegram_id, db_session
                )

        except IntegrityError as e:
            await db_session.rollback()
            logging.error(f"Database integrity error: {e}")
            return cls.create_response("error", message="Database error") 
        except Exception as e:
            logging.error(f"Authentication error: {e}", exc_info=True)
            return cls.create_response("error", message=str(e))  


