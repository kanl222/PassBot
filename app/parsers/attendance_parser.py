import datetime
from functools import lru_cache
import re

import pandas as pd
from .html_parser import HTMLParser
import logging
from typing import Any, List, Dict, Optional
from bs4 import BeautifulSoup, ResultSet, Tag

from app.tools.support import log_html


class AttendanceParser(HTMLParser):

    @staticmethod
    @lru_cache(100)
    def _extract_status_from_class(class_names: tuple) -> str:
        """
        Map CSS classes to attendance status.

        Args:
            class_names: Tuple of CSS class names.

        Returns:
            Attendance status string.
        """
        class_mapping: Dict[str, str] = {
            'cl-grn': 'present',
            'cl-gray': 'absent',
            'cl-or': 'late',
            'cl-red': 'violation',
            'cl-wh': 'unknown',
            'cl-yell': 'unknown',
            'cl-bl':'violation',
            'cl-dbl':'violation',
        }
        return [*list(map(lambda key: class_mapping[key], class_names)), 'unknown']

    @classmethod
    def _handler_statues(cls, statuses: list) -> str:
        return next(
            (
                status
                for status in ('present', 'violation', 'late', 'absent')
                if status in set(statuses)
            ),
            'unknown',
        )

    @classmethod
    def _parse_multiline_rows(cls, multiline_div: Tag) -> str:
        """
        Parse nested attendance details in multiline rows.

        Args:
            multiline_div: BeautifulSoup object of multiline rows container.

        Returns:
            Aggregated attendance status as a string.
        """
        statuses = []
        status = None
        for row in multiline_div.find_all('div', class_='multiline-rows-state'):
            for row_ in row.find_all('div', class_='block-visit'):
                statuses += [cls._handler_statues(
                    cls._extract_status_from_class(tuple(row_.get('class', []))[1:]))]
    
        return cls._handler_statues(statuses)

    @classmethod
    def _parse_line_rows(cls, line_div: Tag) -> str:
        """
        Parse nested attendance details in multiline rows.

        Args:
            multiline_div: BeautifulSoup object of multiline rows container.

        Returns:
            Aggregated attendance status as a string.
        """
        statuses = [stat.get('class', [])[1]
                    for stat in line_div.find_all('div', class_='block-visit')]
        return cls._handler_statues(cls._extract_status_from_class(tuple(set(statuses))))

    @classmethod
    def _parse_single_cell(cls, cell,header_data) -> List[Dict[str, str]]:
        """
        Parse a single attendance cell.

        Args:
            cell: BeautifulSoup object of the cell.

        Returns:
            List of dictionaries with parsed status and details.
        """
        
        user_link = cell.find('a', href=True)[
            'href'] if cell.find('a', href=True) else None
        cells = []
        kodstud = cls.parse_query_param(
            user_link, 'kodstud') if user_link else None
        _cells = cell.find_all('td')[2:]
        for row in range(len(_cells)):
            td=  _cells[row]
            date,pair_number,discipline,type_pair = header_data[row+1]
            status = None
            details = None
            if td.find('div', class_='multi_visit_container'):
                status = cls._parse_multiline_rows(td)
                details = td.find(
                    'div', class_='multiline-rows-state').get('title', '').strip().split('\n')[-1]
            else:
                status = cls._parse_line_rows(td)
                details = td.get('title', '').strip().split('\n')[-1]
            cells += [{
                "date":date, "pair_number":pair_number, "discipline":discipline, "type_pair":type_pair,
                'kodstud': int(kodstud),
                'status': status,
                'details': details
            }]
        return cells
    
    @classmethod
    @log_html
    def parse_attendance(cls, html_content: str) -> List[Dict[str, Any]]:
        """
        Parse the attendance table from the HTML.

        Returns:
            Parsed table as a list of dictionaries.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        table = soup.find("table",class_="table-visits")
        if not table:
            raise ValueError(
                "No table with class 'table-visits' found in the HTML.")

        if table.find(
            "td", rowspan="4", string="За указанный период пары отсутствуют!"
        ):
            logging.info("No pairs found for the specified period.")
            return pd.DataFrame() 

        header_rows: ResultSet[Tag] = table.select("tr.thead")
        header_data = []
        for row in header_rows:
            cells = row.select("td:not([rowspan])")
            row_data = []
            for cell in cells:
                text = cell.get_text(strip=True)


                if match := re.match(r"(\d{2}\.\d{2}\.\d{4}), (\w{2})\.", text):
                    colspan = int(cell.get("colspan", 1))
                    date_obj = datetime.datetime.strptime(match[1], "%d.%m.%Y").date()
                    row_data.extend([date_obj] * colspan)
                else:
                    row_data.append(text)
            header_data.append(row_data)
        header_data = list(zip(*header_data))
        data = []
        for tr in table.find_all("tr")[4:]:
            data.extend(cls._parse_single_cell(tr,header_data))
        df = pd.DataFrame(data)
        df["key_pair"] = pd.to_datetime(df['date']).astype('int64') // 10**9 + df["pair_number"].astype(int)
        return df

