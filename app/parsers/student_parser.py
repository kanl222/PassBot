from typing import Any, List, Dict, Optional
from urllib.parse import ParseResult, urlparse, parse_qs
from bs4 import BeautifulSoup, NavigableString, Tag
from aiohttp import ClientResponse
import logging
from .support import HTMLParser
from app.db.models.users import UserRole


class StudentParser(HTMLParser):
    @classmethod
    async def parse_students_list(cls, html_content: str) -> List[Dict[str, Any]]:
        """
        Parse a list of students from an HTML response.
        
        Args:
            html_content: HTML response containing student list.
        
        Returns:
            List of student dictionaries.
        """
        try:
            
            soup = BeautifulSoup(html_content, 'lxml')
            table: Tag | NavigableString | None = soup.find('table', {"class": "table-visits"})
            
            if not table:
                logging.warning("No student table found")
                return []

            students = []
            for row in table.find_all('tr')[4:]: 
                user_name_tag = row.find('td', {'colspan': 2})
                user_link_tag = row.find('a', href=True)

                if not user_name_tag or not user_link_tag:
                    continue

                full_name: str | None = cls.safe_extract_text(user_name_tag)
                user_link = user_link_tag['href']

                user_id: str | None = cls.parse_query_param(user_link, 'stud')
                kodstud: str | None = cls.parse_query_param(user_link, 'kodstud')

                if user_id and kodstud:
                    students.append({
                        "id_stud": int(user_id),
                        "kodstud": int(kodstud),
                        "full_name": full_name,
                    })

            return students

        except Exception as e:
            logging.error(f"Error parsing students list: {e}")
            return []

    @classmethod
    async def parse_student(cls, html_content: str) -> Dict[str, Any]:
        """
        Parse individual student data from HTML response.
        
        Args:
            html_content: HTML response containing student profile.
        
        Returns:
            Dictionary with student information.
        
        Raises:
            ValueError: If critical student information cannot be parsed.
        """
        try:
            soup = BeautifulSoup(html_content, 'lxml')
            table_info: Tag | NavigableString | None = soup.find("div", id="title_info")

            if not table_info:
                raise ValueError("Student information block not found")

            name_tags = table_info.find_all("p")
            if len(name_tags) < 2:
                raise ValueError("Insufficient student information")

            name_tag = name_tags[1].find("b")
            if full_name := cls.safe_extract_text(name_tag):
                return {
                    "full_name": full_name,
                    "role": UserRole.STUDENT
                }

            else:
                raise ValueError("Student name could not be extracted")

        except ValueError as ve:
            logging.error(f"Student parsing error: {ve}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error parsing student: {e}")
            raise
