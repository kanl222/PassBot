from typing import Optional
from urllib.parse import ParseResult, urlparse, parse_qs
from bs4 import Tag

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