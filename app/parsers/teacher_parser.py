from bs4 import BeautifulSoup
from aiohttp import ClientResponse
from ..db.models.users import User, UserRole
import logging



async def parse_teacher(response: ClientResponse) -> User:
    """
    Parses teacher data from HTML

    :param response: ClientResponse object with HTML page of the teacher profile.
    :return: User object representing the teacher.
    """
    try:
        # Парсинг HTML страницы
        soup = BeautifulSoup(await response.text(), 'lxml')
        name_tag = soup.find("div", id="title_info").find("p").find("b")
        if not name_tag:
            raise ValueError("Unable to find element with teacher name. Please check your HTML.")
        name = name_tag.get_text(strip=True)

        user = User(
            full_name=name,
            role=UserRole.TEACHER
        )

        return user

    except Exception as e:
        logging.error(f"Parsing or saving error teacher: {e}")
        raise
