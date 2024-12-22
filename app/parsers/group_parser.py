from typing import List, Dict, Optional
from bs4 import BeautifulSoup, NavigableString, Tag
import json
import logging
from .support import HTMLParser


class GroupParser(HTMLParser):
    @classmethod
    def parse_groups(cls, html_content: str) -> List[Dict[str, str]]:
        """
        Parse group information from HTML content.
        
        Args:
            html_content: HTML string containing group information.
        
        Returns:
            List of dictionaries with group details.
        """
        try:
            soup = BeautifulSoup(html_content, 'lxml')
            table: Tag | NavigableString | None = soup.find('table')
            
            if not table:
                logging.warning("No table found in HTML content")
                return []

            group_data = []
            group_rows = table.find_all('tr')
            
            for row in group_rows:
                cells = row.find_all('td', class_='va-baseline padding-small limit-width')
                
                for cell in cells:
                    group_link = cell.find('a')
                    if not group_link:
                        continue

                    group_name: str | None = cls.safe_extract_text(group_link)
                    group_id = group_link.get('href', '').split('=')[-1]

                    if group_name and group_id:
                        group_data.append({
                            'name': group_name,
                            'id': group_id
                        })

            return group_data

        except Exception as e:
            logging.error(f"Error parsing groups: {e}")
            return []