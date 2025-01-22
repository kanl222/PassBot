import logging
from typing import Dict, Any

from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import crypto
from app.db.crud.users import get_student, create_user 
from app.db.db_session import with_session
from app.db.models.users import Student, UserRole, Teacher
from app.parsers.student_parser import StudentParser
from app.parsers.teacher_parser import TeacherParser
from app.parsers.urls import link_to_login
from app.session.session_manager import SessionManager, is_teacher


class AuthService:  # Renamed class
    @staticmethod
    def create_response(status: str, **kwargs) -> Dict[str, Any]:
        """Create a standardized response dictionary."""
        return {"status": status, **kwargs}

    @staticmethod
    async def _register_teacher(
        session_manager: SessionManager,
        telegram_id: int,
        login: str,
        password: str,
        db_session: AsyncSession,
    ) -> Dict[str, Any]:
        """Registers a teacher."""

        async with await session_manager.get(link_to_login) as response:  
            teacher_data = await TeacherParser.parse_teacher(await response.text())

        teacher = await create_user(
            db_session,
            full_name=teacher_data["full_name"],
            telegram_id=telegram_id,
            role=UserRole.TEACHER,
            _encrypted_data_user=crypto.encrypt({"login": login, "password": password}),
        )
        return AuthService.create_response(  
            "success", role=teacher.role.value, user=teacher.full_name
        )

    @staticmethod
    async def _register_student(
        session_manager: SessionManager,
        telegram_id: int,
        db_session: AsyncSession,
    ) -> Dict[str, Any]:
        """Registers or updates a student."""

        async with await session_manager.get(link_to_login) as response:
            student_data = await StudentParser.parse_student(await response.text())
        existing_student = await get_student(db_session=db_session,full_name=student_data["full_name"]) 

        if existing_student:
            existing_student.telegram_id = telegram_id
            await db_session.commit()
            return AuthService.create_response(
                "updated", role=existing_student.role.value, user=existing_student.full_name
            )


        await create_user(
            db_session,
            full_name=student_data["full_name"],
            telegram_id=telegram_id,
            role=UserRole.STUDENT,
        )
        return AuthService.create_response(
            "no_group", message="Student registered successfully (group will be assigned by the teacher)."
        ) 

    @staticmethod
    @with_session
    async def authenticate_user(
        user_input_data: dict, db_session: AsyncSession
    ) -> dict:
        """Authenticates a user."""

        login, password, telegram_id = (
            user_input_data["login"],
            user_input_data["password"],
            user_input_data["id_user_telegram"],
        )

        try:
            async with SessionManager(login, password) as session_manager:
                if not session_manager.status:
                    return AuthService.create_response(
                        "error", message="Authentication failed", details="Invalid login or password"
                    )

                is_user_teacher = await is_teacher(session_manager)

                if is_user_teacher:
                    return await AuthService._register_teacher(session_manager, telegram_id, login, password, db_session)
                else:
                    return await AuthService._register_student(session_manager, telegram_id, db_session)

        except IntegrityError as e:
            await db_session.rollback()
            logging.error(f"Database integrity error: {e}")
            return AuthService.create_response("error", message="Database error: User already exists") 
        except Exception as e:
            logging.error(f"Authentication error: {e}", exc_info=True)
            return AuthService.create_response("error", message=f"An unexpected error occurred: {e}")  


