from bs4 import BeautifulSoup
from aiohttp import ClientResponse
from urllib.parse import urlparse, parse_qs
from sqlalchemy.exc import IntegrityError
from ..db.db_session import with_session
from ..db.models.users import User,UserRole
import logging


@with_session
async def parse_students_list(response: ClientResponse, db_session ) -> list[User]:
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



async def parse_student(response: ClientResponse) -> User:
    """
    Parses the student data from the HTML response .

    :param response: The ClientResponse object with the HTML page of the student profile.
    :return: The User object representing the student.
    """
    try:
        soup = BeautifulSoup(await response.text(), 'lxml')
        name_tag = soup.find("div", id="title_info").find("p").find("b")
        if not name_tag:
            raise ValueError("Could not find element named student. Please check your HTML.")

        name = name_tag.get_text(strip=True)

        user = User(
            full_name=name,
            role=UserRole.STUDENT
        )

        return user

    except Exception as e:
        logging.error(f"Student parse error: {e}")
        raise

