from bs4 import BeautifulSoup
from aiohttp import ClientResponse
from urllib.parse import urlparse
from urllib.parse import parse_qs
from sqlalchemy.exc import IntegrityError
from ..models import Group
import logging

async def parse_groups(response: ClientResponse,db_session):
    """
    Parse group data from the HTML response and save it to the database.

    :param response: A ClientResponse object containing the HTML of the groups table.
    :param db_session: SQLAlchemy session for database operations.
    :return: None.
    """
    try:
        soup = BeautifulSoup(await response.text(), 'lxml')
        rows = soup.find_all('tr')
        groups = []

        for row in rows:
            group_name_tag = row.find('td', class_='limit-width')
            if group_name_tag:
                group_name = group_name_tag.get_text(strip=True)
                group_link_tag = row.find('a', href=True)

                if group_link_tag:
                    group_link = group_link_tag['href']
                    parsed_url = urlparse(group_link)
                    group_id = parse_qs(parsed_url.query).get('group_id', [None])[0]

                    if group_id:
                        group = Group(group_name=group_name, group_id=group_id)
                        groups.append(group)

        # Сохранение в базу данных
        for group in groups:
            try:
                db_session.add(group)
                db_session.commit()
                logging.info(f"Group {group.group_name} saved to the database.")
            except IntegrityError:
                db_session.rollback()
                logging.error(f"Group {group.group_name} already exists in the database.")

    except Exception as e:
        db_session.rollback()
        raise ValueError(f"Error parsing or saving groups: {e}")


