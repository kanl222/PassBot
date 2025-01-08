from typing import Dict, Any
from bs4 import BeautifulSoup, NavigableString, Tag
from aiohttp import ClientResponse
import logging

from app.db.models.users import UserRole
from .html_parser import HTMLParser



class TeacherParser(HTMLParser):
    @classmethod
    async def parse_teacher(cls, html_content: str) -> Dict[str, Any]:
        """
        Parse teacher data from HTML response.

        Args:
            response: HTML response containing teacher profile.

        Returns:
            Dictionary with teacher information.

        Raises:
            ValueError: If critical teacher information cannot be parsed.
        """
        try:
            soup = await cls.get_soup(html_content)
            title_info: Tag | NavigableString | None = soup.find(
                "div", id="title_info")

            if not title_info:
                raise ValueError("Teacher information block not found")

            name_tags = title_info.find_all("p")
            if len(name_tags) < 2:
                raise ValueError("Insufficient teacher information")

            name_tag = name_tags[1].find("b")
            if full_name := cls.safe_extract_text(name_tag):
                return {
                    "full_name": full_name,
                    "role": UserRole.TEACHER
                }

            else:
                raise ValueError("Teacher name could not be extracted")

        except ValueError as ve:
            logging.error(f"Teacher parsing error: {ve}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error parsing teacher: {e}")
            raise
