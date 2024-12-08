from bs4 import BeautifulSoup
from aiohttp import ClientResponse
from urllib.parse import urlparse, parse_qs
from sqlalchemy.exc import IntegrityError
from ..db.db_session import with_session
from ..models import User,UserRole
import logging


@with_session
async def parse_users(response: ClientResponse, db_session ) -> list[User]:
    """
    Parses user data from the HTML response and stores it in the database.

    :param response: A ClientResponse object containing HTML with user data.
    :param db_session: A SQLAlchemy session for database operations.
    :return: None.
    """
    try:
        soup = BeautifulSoup(await response.text(), 'lxml')
        rows = soup.find_all('tr')
        users = []

        for row in rows:
            user_name_tag = row.find('td', class_='limit-width')
            if user_name_tag:
                user_name = user_name_tag.get_text(strip=True)

                user_link_tag = row.find('a', href=True)
                if user_link_tag:
                    user_link = user_link_tag['href']
                    parsed_url = urlparse(user_link)
                    user_id = parse_qs(parsed_url.query).get('stud', [None])[0]
                    kodstud = parse_qs(parsed_url.query).get('kodstud', [None])[0]

                    if user_id and kodstud:
                        user = User(
                            user_name=user_name,
                            user_id=user_id,
                            kodstud=kodstud
                        )
                        users.append(user)

        for user in users:
            try:
                db_session.add(user)
                db_session.commit()
                logging.info(f"Пользователь {user.user_name} сохранён в базе данных.")
            except IntegrityError:
                db_session.rollback()
                logging.warning(f"Пользователь {user.user_name} уже существует в базе данных.")
        return users
    except Exception as e:
        logging.error()


@with_session
async def parse_student(response: ClientResponse, db_session) -> User:
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
            role=UserRole.Student
        )

        return user

    except Exception as e:
        db_session.rollback()
        logging.error(f"Error parsing or saving teacher: {e}")
        raise


