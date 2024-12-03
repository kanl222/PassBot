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
    Анализирует данные пользователей из HTML-ответа и сохраняет их в базе данных.

    :param response: Объект ClientResponse, содержащий HTML с данными пользователей.
    :param db_session: Сеанс SQLAlchemy для операций с базой данных.
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
