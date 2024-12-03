from bs4 import BeautifulSoup
from aiohttp import ClientResponse
from urllib.parse import urlparse, parse_qs
from sqlalchemy.exc import IntegrityError
from ..db.db_session import with_session
from ..models import User
import logging

@with_session
async def parse_teacher(data_user:dict, db_session):
    """
    Анализирует данные пользователей из HTML-ответа и сохраняет их в базе данных.

    :param response: Объект ClientResponse, содержащий HTML с данными пользователей.
    :param db_session: Сеанс SQLAlchemy для операций с базой данных.
    :return: None.
    """
    try:
        soup = BeautifulSoup(await response.text(), 'lxml')
        name = soup.find(id="fio_holder").text

        try:
            db_session.add(user)
            db_session.commit()
            logging.info(f"Пользователь {user.user_name} сохранён в базе данных.")
        except IntegrityError:
            db_session.rollback()
            logging.warning(f"Пользователь {user.user_name} уже существует в базе данных.")
