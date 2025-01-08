from typing import Optional
from urllib.parse import ParseResult, urlparse, parse_qs
from bs4 import BeautifulSoup, Tag
import bs4

class HTMLParser:
    @staticmethod
    def safe_extract_text(element: Optional[Tag], strip: bool = True) -> Optional[str]:
        """Safely extract text from a BeautifulSoup element."""
        return element.get_text(strip=strip) if element else None

    @staticmethod
    def parse_query_param(url: str, param: str) -> Optional[str]:
        """Parse a specific query parameter from a URL."""
        parsed_url: ParseResult = urlparse(url)
        return parse_qs(parsed_url.query).get(param, [None])[0]
    
    @classmethod
    def get_soup(cls, html_content: str, parser: str = "html.parser") -> BeautifulSoup:  # Added parser argument
        """Create a BeautifulSoup object with the specified parser."""
        return BeautifulSoup(html_content, parser)