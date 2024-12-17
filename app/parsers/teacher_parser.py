from bs4 import BeautifulSoup
from aiohttp import ClientResponse
from app.db.models.users import User, UserRole
import logging

async def parse_teacher(response: ClientResponse) -> dict:
    """
    Parses teacher data from the HTML response and returns it as a dictionary.

    :param response: A ClientResponse object containing HTML with teacher data.
    :return: A dictionary representing the parsed teacher.
    """
    try:
        soup = BeautifulSoup(await response.text(), 'lxml')
        name_tag = soup.find("div", id="title_info").find_all("p")[1].find("b")
        if not name_tag:
            raise ValueError("Unable to find element with teacher name. Please check your HTML.")

        full_name = name_tag.get_text(strip=True)

        teacher = {
            "full_name": full_name,
            "role": UserRole.TEACHER
        }

        return teacher

    except Exception as e:
        logging.error(f"Parsing error for teacher: {e}")
        raise
