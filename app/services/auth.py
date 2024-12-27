import logging
from typing import Dict, Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select

from app.services.users import get_student
from app.session.session_manager import is_teacher, SessionManager
from app.parsers.urls import link_to_login
from app.parsers.teacher_parser import TeacherParser
from app.parsers.student_parser import StudentParser
from app.db.db_session import with_session
from app.db.models.users import Student, User, UserRole, Teacher
from app.core.security import crypto


def create_response(status: str, **kwargs) -> Dict[str, Any]:
    """Create a standardized response dictionary."""
    base_response: Dict[str, str] = {"status": status} | kwargs
    return base_response



async def _handle_teacher_registration(sm, user_data, login, password, telegram_id, db_session) -> Dict[str, Any]:
    """Handles the registration process for a teacher in the authentication system.

    This function parses teacher data, updates user information, and registers the teacher in the database.

    Args:
        sm: The session manager for authentication.
        user_data (dict): A dictionary containing user information.
        login (str): The teacher's login credentials.
        password (str): The teacher's password.
        telegram_id (int): The teacher's Telegram ID.
        db_session: The database session for performing registration.

    Returns:
        dict: A response dictionary indicating the result of the teacher registration.
    """
    response = await sm.session.get(link_to_login)
    teacher_data: Dict[str, Any] = await TeacherParser.parse_teacher(await response.text())
    user_data.update(teacher_data)
    user_data["role"] = UserRole.TEACHER

    await register_teacher(user_data, login, password, telegram_id, db_session)
    return create_response(
        "success",
        role=user_data["role"].value,
        user=user_data["full_name"]
    )


async def _handle_student_registration(sm, user_data, telegram_id, db_session) -> Dict[str, Any]:
    """Handles the registration process for a student in the authentication system.

    This function parses student data, checks for existing students, and registers new students in the database.

    Args:
        sm: The session manager for authentication.
        user_data (dict): A dictionary containing user information.
        telegram_id (int): The student's Telegram ID.
        db_session: The database session for performing registration.

    Returns:
        dict: A response dictionary indicating the result of the student registration.
    """
    response = await sm.session.get(link_to_login)
    student_data: Dict[str, Any] = await StudentParser.parse_student(await response.text())
    user_data.update(student_data)
    user_data["role"] = UserRole.STUDENT
    existing_student = await get_student(full_name=user_data['full_name'])
    print(existing_student)
    if existing_student:
        if existing_student := existing_student[0]:
            existing_student.telegram_id = telegram_id
            await db_session.commit()
            return create_response(
                "updated",
                role=existing_student.role.value,
                user=existing_student.full_name
            )

    new_student = Student(
        full_name=student_data["full_name"],
        role=UserRole.STUDENT,
        telegram_id=telegram_id
    )
    db_session.add(new_student)
    await db_session.commit()

    return create_response(
        "no_group",
        message="The teacher has not registered a group for this student."
    )


@with_session
async def authenticated_users(user_input_data: dict, db_session) -> dict:
    """Authenticates and registers users in the system based on their credentials.

    This function manages the authentication process for both teachers and students, handling various scenarios such as login validation, role determination, and database registration.

    Args:
        user_input_data (dict): A dictionary containing user authentication credentials.
        db_session: The database session for performing authentication and registration.

    Returns:
        dict: A response dictionary containing the authentication and registration result.

    Raises:
        IntegrityError: If there is a database integrity issue during registration.
        Exception: For any unexpected errors during the authentication process.
    """
    login, password, telegram_id = (
        user_input_data['login'],
        user_input_data['password'],
        user_input_data['id_user_telegram']
    )

    try:
        async with SessionManager(login, password) as sm:
            if not sm or not sm.status:
                return create_response(
                    "error",
                    message="Authentication failed",
                    details="Invalid login or password"
                )

            user_data: Dict[str, None] = {"full_name": None, "role": None}

            if await is_teacher(sm.session):
                return await _handle_teacher_registration(sm, user_data, login, password, telegram_id, db_session)

            return await _handle_student_registration(sm, user_data, telegram_id, db_session)

    except IntegrityError as e:
        await db_session.rollback()
        logging.error(f"Database integrity error: {e}")
        return create_response("error", message="Database error")
    except Exception as e:
        logging.error(f"Authentication error: {e}", exc_info=True)
        return create_response("error", message=str(e))



async def register_teacher(teacher_data: dict, login: str, password: str, telegram_id: int, db_session) -> None:
    """Registers a teacher in the system's database.

    This function creates a new Teacher instance and commits it to the database.

    Args:
        teacher_data (dict): A dictionary containing teacher information.
        login (str): The teacher's login credentials.
        password (str): The teacher's password.
        telegram_id (int): The teacher's Telegram ID.
        db_session: The database session for performing registration.
    """
    
    
    teacher = Teacher(
        full_name=teacher_data["full_name"],
        telegram_id=telegram_id,
        _encrypted_data_user=crypto.encrypt({
            'login':login,
            'password':password
        }),
        role = UserRole.TEACHER
    )

    db_session.add(teacher)
    await db_session.commit()
    logging.info(f"Teacher {teacher.full_name} is registered.")