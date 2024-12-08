from bs4 import BeautifulSoup
from aiohttp import ClientResponse
from sqlalchemy.exc import IntegrityError
from ..db.db_session import with_session
from ..models.sqlalchemy.users import User,UserRole
import logging


@with_session
async def parse_teacher(response: ClientResponse, db_session) -> User:
    """
    Parses teacher data and saves it to the database.

    :param response: ClientResponse object with HTML page of teacher profile.
    :param data_user: Dictionary with user data (login, password).
    :param db_session: SQLAlchemy session for database operations.
    """
    try:
        soup = BeautifulSoup(await response.text(), 'lxml')
        name_tag = soup.find("div", id="title_info").find("p").find("b")
        if not name_tag:
            raise ValueError("Could not find element with id 'fio_holder'. Please check HTML version.")

        name = name_tag.get_text(strip=True)


        user = User(
            full_name=name,
            role=UserRole.TEACHER
        )

        return user

    except Exception as e:
        db_session.rollback()
        logging.error(f"Error parsing or saving teacher: {e}")
        raise
