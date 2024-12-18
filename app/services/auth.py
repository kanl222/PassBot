from typing import Any
from ..session.session_manager import is_teacher,SessionManager
from ..parsers.urls import link_to_login
import logging
from ..core.security import encode_dict
from ..parsers.teacher_parser import parse_teacher
from ..parsers.student_parser import parse_student
from ..db.db_session import with_session
from app.db.models.users import User, UserRole, Teacher
from app.db.models.groups import Group
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select

@with_session
async def authenticated_users(user_input_data: dict, db_session) -> dict:
    """
    Authenticates the user based on the provided credentials and registers the user.

    Args:
        user_input_data (dict): A dictionary containing the user's credentials.
        db_session: The SQLAlchemy session for database operations.

    Returns:
        dict: The result of the authentication and registration process.
    """
    login = user_input_data['login']
    password = user_input_data['password']
    telegram_id = user_input_data['id_user_telegram']

    try:
        async with SessionManager(login, password) as sm:
            if not sm or not sm.status:
                logging.error(f"Authentication failed for user {login}. Invalid session.")
                return {
                    "status": "error",
                    "message": "Authentication failed",
                    "details": "Invalid login or password"
                }

            async with await sm.session.get(link_to_login) as response:
                if response.status == 200:
                    logging.info(f"Authentication successful for user: {login}")
                    user_data = {"full_name": None, "role": None}

                    if await is_teacher(sm.session):
                        teacher_data = await parse_teacher(response)
                        user_data.update(teacher_data)
                        user_data["role"] = UserRole.TEACHER

                        await register_teacher(user_data, login, password, telegram_id, db_session)
                        return {
                            "status": "success",
                            "role": user_data["role"].value,
                            "user": user_data["full_name"]
                        }

                    student_data = await parse_student(response)
                    user_data.update(student_data)
                    user_data["role"] = UserRole.STUDENT

                    existing_student = await db_session.execute(
                        select(User).filter(User.full_name == student_data["full_name"], User.role == UserRole.STUDENT)
                    )
                    existing_student = existing_student.scalar()

                    if existing_student:
                        existing_student.telegram_id = telegram_id
                        await db_session.commit()
                        logging.info(f"Updated Telegram ID for existing student: {existing_student.full_name}.")
                        return {
                            "status": "updated",
                            "role": existing_student.role.value,
                            "user": existing_student.full_name
                        }

                    new_student = User(
                        full_name=student_data["full_name"],
                        role=UserRole.STUDENT,
                        telegram_id=telegram_id
                    )
                    db_session.add(new_student)
                    await db_session.commit()

                    logging.warning(f"Group for student {new_student.full_name} not found.")
                    return {
                        "status": "no_group",
                        "message": "The teacher has not registered a group for this student."
                    }


                else:
                    error_details = await response.text()
                    logging.error(f"Authentication failed for user: {login}. Error: {error_details}")
                    return {
                        "status": "error",
                        "message": "Authentication failed",
                        "details": error_details
                    }

    except IntegrityError as e:
        await db_session.rollback()
        logging.error(f"Database integrity error: {e}")
        return {"status": "error", "message": "Database error"}
    except Exception as e:
        logging.error(f"An error occurred during authentication: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


@with_session
async def register_teacher(teacher_data: dict, login: str, password: str, telegram_id: int, db_session) -> None:
    """
    Registers a teacher in the system.

    Args:
        teacher_data (dict): Teacher data.
        login (str): Teacher login.
        password (str): Teacher password.
        telegram_id (int): Telegram ID of the teacher.
        db_session: SQLAlchemy session for database operations.

    Returns:
        None
    """
    try:
        teacher = Teacher(
            full_name=teacher_data["full_name"],
            telegram_id=telegram_id,
            _encrypted_data_user=await encode_dict({
            'login': login,
            'password': password
        })
        )

    db_session.add(teacher)
    await db_session.commit()
    logging.info(f"Teacher {teacher.full_name} is registered.")

@with_session
async def check_user_in_db(telegram_id,db_session) -> dict[str, Any]:
    """
    Check if a user exists in the database by their Telegram ID.

    Args:
        db_session: SQLAlchemy Async Session to interact with the database.
        telegram_id: Telegram ID of the user to check.

    Returns:
        dict: Information about the user's existence status, full name, and role.
    """
    try:
        # Query the database for a user with the given Telegram ID
        result = await db_session.execute(
            select(User).filter(User.telegram_id == telegram_id)
        )
        existing_user = result.scalar()

        if existing_user:
            logging.info(f"User with Telegram ID {telegram_id} already exists: {existing_user.full_name}.")
            return {
                "status": "exists",
                "user": existing_user.full_name,
                "role": existing_user.role.value
            }
        else:
            logging.info(f"No user found with Telegram ID {telegram_id}.")
            return {
                "status": "not_found",
                "user": None,
                "role": None
            }
    except Exception as e:
        logging.error(f"An error occurred while checking user in database: {e}")
        return {
            "status": "error",
            "user": None,
            "role": None,
            "error_message": str(e)
        }
