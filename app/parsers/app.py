from ..session.session_manager import get_user_session, is_teacher
from .urls import link_to_login
import logging
from .parsers.teacher_parser import parse_teacher
from .parsers.student_parser import parse_student
from ..db.db_session import with_session
from app.db.models.users import User, UserRole, Teacher
from app.db.models.groups import Group
from sqlalchemy.exc import IntegrityError

user_input_data = {
    'id_user_telegram': 32423423,  # Telegram ID пользователя
    'password': '324234',  # Пароль в открытом виде
    'login': 'ekjojrow',  # Логин пользователя
}


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
        # Проверяем, существует ли пользователь в базе данных
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

                    user_data = {
                        "full_name": None,
                        "role": None
                    }

                    if await is_teacher(sess):
                        teacher_data = await parse_teacher(response)
                        user_data.update(teacher_data)
                        user_data["role"] = UserRole.TEACHER

                        await register_teacher(user_data, login, password, telegram_id, db_session)

                        return {
                            "status": "success",
                            "role": user_data["role"].value,
                            "user": user_data["full_name"]
                        }
                    else:
                        student_data = await parse_student(response)
                        user_data.update(student_data)
                        user_data["role"] = UserRole.STUDENT

                        user = User(
                            full_name=user_data["full_name"],
                            role=user_data["role"],
                            telegram_id=telegram_id,
                            _login=login,
                            _encrypted_password=password
                        )

                        db_session.add(user)
                        db_session.commit()

                        group = await db_session.execute(
                            db_session.query(Group).filter_by(id=user.group_id)
                        )
                        group = group.scalar()

                        if not group:
                            logging.warning(f"Group for student {user.full_name} not found.")
                            return {
                                "status": "no_group",
                                "message": "The teacher has not registered a group for this student."
                            }

                        logging.info(
                            f"User {user.full_name} ({user.role.value}) is registered with group {group.name}.")
                        return {
                            "status": "success",
                            "role": user.role.value,
                            "user": user.full_name
                        }
                else:
                    # Ошибка аутентификации
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
    teacher = Teacher(
        full_name=teacher_data["full_name"],
        telegram_id=telegram_id,
        _login=login,
        _encrypted_password=password
    )

    db_session.add(teacher)
    db_session.commit()
    logging.info(f"Teacher {teacher.full_name} is registered.")


@with_session
async def get_student_group(full_name: str, db_session) -> dict:
    """
    Gets student group information given a full name.

    Args:
        full_name (str): Student's full name.
        db_session: SQLAlchemy session for database operations.

    Returns:
        dict: Student group information or error message.
    """
    try:
        student = await db_session.execute(
            db_session.query(User).filter_by(full_name=full_name, role=UserRole.STUDENT)
        )
        student = student.scalar()

        if not student:
            logging.warning(f"Student with name {full_name} not found.")
            return {"status": "not_found", "message": "Student not found."}

        group = await db_session.execute(
            db_session.query(Group).filter_by(id=student.group_id)
        )
        group = group.scalar()

        if not group:
            logging.warning(f"Group for student {full_name} not found.")
            return {"status": "no_group", "message": "Group not found for the student."}

        logging.info(f"Group {group.name} found for student {full_name}.")
        return {"status": "success", "group": group.name}

    except Exception as e:
        logging.error(f"An error occurred while fetching group for {full_name}: {e}")
        return {"status": "error", "message": str(e)}
