from bs4 import BeautifulSoup
from aiohttp import ClientResponse
from sqlalchemy.exc import IntegrityError
from ..db.db_session import with_session
from ..models.sqlalchemy.users import User,UserRole
import logging


@with_session
async def parse_teacher(response: ClientResponse, data_user: dict, db_session):
    """
    Parses teacher data and saves it to the database.

    :param response: ClientResponse object with HTML page of teacher profile.
    :param data_user: Dictionary with user data (login, password).
    :param db_session: SQLAlchemy session for database operations.
    """
    try:
        soup = BeautifulSoup(await response.text(), 'lxml')
        name_tag = soup.find(id="fio_holder")
        if not name_tag:
            raise ValueError("Не удалось найти элемент с id 'fio_holder'. Проверьте структуру HTML.")

        name = name_tag.get_text(strip=True)

        login = data_user.get('login')
        password = data_user.get('password')

        if not login or not password:
            raise ValueError("Логин и пароль обязательны для сохранения преподавателя.")

        user = User(
            full_name=name,
            telegram_id=None,
            _login=login,
            _encrypted_password=password,
            role=UserRole.TEACHER
        )

        try:
            db_session.add(user)
            db_session.commit()
            logging.info(f"Преподаватель {user.full_name} сохранён в базе данных.")
        except IntegrityError:
            db_session.rollback()
            logging.warning(f"Преподаватель {user.full_name} уже существует в базе данных.")

    except Exception as e:
        db_session.rollback()
        logging.error(f"Ошибка парсинга или сохранения преподавателя: {e}")
        raise
