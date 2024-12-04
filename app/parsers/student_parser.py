from bs4 import BeautifulSoup
from aiohttp import ClientResponse
from urllib.parse import urlparse, parse_qs
from sqlalchemy.exc import IntegrityError
from ..db.db_session import with_session
from ..models import User
import logging


@with_session
async def parse_users(response: ClientResponse, db_session):
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
