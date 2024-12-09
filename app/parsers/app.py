from ..session.session_manager import get_user_session, is_teacher
from .urls import link_to_login
import logging
from .teacher_parser import parse_teacher
from .student_parser import parse_student
from ..db.db_session import with_session
from app.db.models.users import User
from sqlalchemy.exc import IntegrityError


@with_session
async def authenticated_users(user_input_data: dict, db_session) -> dict:
    """
    Authenticates a user based on provided credentials and registers them.

    Args:
        user_input_data (dict): Dictionary containing user credentials.
        db_session: SQLAlchemy session for database operations.

    Returns:
        dict: Result of the authentication and registration process.
    """
    login = user_input_data['login']
    password = user_input_data['password']
    telegram_id = user_input_data['id_user_telegram']

    try:
        existing_user = await db_session.execute(
            db_session.query(User).filter_by(telegram_id=telegram_id)
        )
        existing_user = existing_user.scalar()

        if existing_user:
            logging.info(f"User with Telegram ID {telegram_id} already exists: {existing_user.full_name}.")
            return {
                "status": "exists",
                "user": existing_user.full_name,
                "role": existing_user.role.value
            }

        async with get_user_session(login, password) as sess:
            async with sess.get(link_to_login) as response:
                if response.status == 200:
                    logging.info(f"Authentication successful for user: {login}")
                    if await is_teacher(sess):

                        teacher = await parse_teacher(response, db_session)
                        teacher.telegram_id = telegram_id
                        teacher._login = login
                        teacher._encrypted_password = password
                        db_session.add(teacher)
                        db_session.commit()
                        logging.info(f"Teacher {teacher.full_name} is registered.")
                        return {
                            "status": "success",
                            "role": "teacher",
                            "user": teacher.full_name
                        }
                    else:
                        student = await parse_student(response, db_session)
                        student.telegram_id = telegram_id
                        db_session.add(student)
                        db_session.commit()
                        logging.info(f"Student {student.full_name} is registered.")
                        return {
                            "status": "success",
                            "role": "student",
                            "user": student.full_name
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
        db_session.rollback()
        logging.error(f"Database integrity error: {e}")
        return {"status": "error", "message": "Database error"}
    except Exception as e:
        logging.error(f"An error occurred during authentication: {e}")
        return {"status": "error", "message": str(e)}
