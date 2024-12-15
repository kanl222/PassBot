from bs4 import BeautifulSoup
from aiohttp import ClientResponse
from urllib.parse import urlparse, parse_qs
from ...db.models.users import Student, UserRole
import logging

async def parse_students_list(response: ClientResponse) -> list[dict]:
    """
    Parses user data from the HTML response and returns it as a list of dictionaries.

    :param response: A ClientResponse object containing HTML with user data.
    :return: A list of dictionaries with student data.
    """
    try:
        soup = BeautifulSoup(await response.text(), 'lxml')
        table = soup.find('table', {"class": "table-visits"})
        rows = table.find_all('tr')
        students = []

        for row in rows[4:]:  # Пропускаем заголовки таблицы
            user_name_tag = row.find('td', {'colspan': 2})
            if user_name_tag:
                full_name = user_name_tag.get_text(strip=True)

                user_link_tag = row.find('a', href=True)
                if user_link_tag:
                    user_link = user_link_tag['href']
                    parsed_url = urlparse(user_link)
                    user_id = parse_qs(parsed_url.query).get('stud', [None])[0]
                    kodstud = parse_qs(parsed_url.query).get('kodstud', [None])[0]

                    if user_id and kodstud:
                        student = {
                            "id_stud": int(user_id),
                            "kodstud": int(kodstud),
                            "full_name": full_name,
                            "role": UserRole.STUDENT
                        }
                        students.append(student)

        return students

    except Exception as e:
        logging.error(f"Ошибка при разборе списка студентов: {e}")
        return []


async def parse_student(response: ClientResponse) -> dict:
    """
    Parses the student data from the HTML response and returns it as a dictionary.

    :param response: The ClientResponse object with the HTML page of the student profile.
    :return: A dictionary representing the parsed student.
    """
    try:
        soup = BeautifulSoup(await response.text(), 'lxml')
        table_info = soup.find("div", id="title_info")

        if not table_info:
            raise ValueError("Не найден блок с информацией о студенте.")

        name_tag = table_info.find("p").find("b")
        if not name_tag:
            raise ValueError("Не найден элемент с именем студента. Проверьте HTML.")

        full_name = name_tag.get_text(strip=True)

        student = {
            "full_name": full_name,
            "role": UserRole.STUDENT
        }

        return student

    except Exception as e:
        logging.error(f"Ошибка при разборе данных студента: {e}")
        raise
