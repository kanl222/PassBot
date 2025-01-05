import datetime
from html.parser import HTMLParser
from typing import Any, List, Dict, Optional
from urllib.parse import ParseResult, parse_qs, urlparse
from bs4 import BeautifulSoup, Tag




class AttendanceParser(HTMLParser):
    @staticmethod
    def parse_query_param(url: str, param: str) -> Optional[str]:
        """Parse a specific query parameter from a URL."""
        return parse_qs(urlparse(url).query).get(param, [None])[0]
    
    @staticmethod
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
        }
        return next((class_mapping[cls] for cls in class_names if cls in class_mapping), 'unknown')

    @classmethod
    def _parse_multiline_rows(cls, multiline_div: Tag) -> str:
        """
        Parse nested attendance details in multiline rows.

        Args:
            multiline_div: BeautifulSoup object of multiline rows container.

        Returns:
            Aggregated attendance status as a string.
        """
        for row in multiline_div.find_all('div', class_='multiline-rows-state'):
            status_ = [
                cls._extract_status_from_class(tuple(row_.get('class', [])))
                for row_ in row.find_all('div', class_='block-visit')
            ]
            if 'present' in status_:
                return 'present'
            elif 'violation' in status_:
                return 'violation'
        return 'absent'
    
    @classmethod
    def _parse_single_cell(cls, cell) -> List[Dict[str, str]]:
        """
        Parse a single attendance cell.

        Args:
            cell: BeautifulSoup object of the cell.

        Returns:
            List of dictionaries with parsed status and details.
        """
        user_link = cell.find('a', href=True)[
            'href'] if cell.find('a', href=True) else None

        kodstud = cls.parse_query_param(user_link, 'kodstud') if user_link else None
        
        return [
            {
                'kodstud': kodstud,
                'status': 
                    cls._parse_multiline_rows(td)
                    if td.find('div', class_='multi_visit_container')
                    else cls._extract_status_from_class(
                        tuple(
                            td.find('div', class_='block-visit').get('class', [])
                        )
                        if td.find('div', class_='block-visit')
                        else ()
                    
                ),
                'details': (
                    td.find('div', class_='multiline-rows-state')
                    .get('title', '')
                    .strip()
                    .split('\n')[-1]
                    if td.find('div', class_='multi_visit_container')
                    else td.get('title', '').strip().split('\n')[-1]
                ),
            }
            for td in cell.find_all('td')[2:]
        ]

    @classmethod
    async def parse_attendance(cls, html_content: str) -> List[Dict[str, Any]]:
        """
        Parse the attendance table from the HTML.

        Returns:
            Parsed table as a list of dictionaries.
        """
        soup = BeautifulSoup(html_content, "lxml")
        table = soup.select_one("table.table-visits")
        if not table:
            raise ValueError(
                "No table with class 'table-visits' found in the HTML.")

        # Parse header rows
        header_rows = table.select("tr.thead")
        header_data = []
        for row in header_rows:
            cells = row.select("td:not([rowspan])")
            row_data = []
            for cell in cells:
                text = cell.get_text(strip=True)
                colspan = int(cell.get('colspan', 1))
                row_data.extend([text] * colspan)
            header_data.append(row_data)

        rows: List[List[Dict[str, str] | str]] = [
            [''] + cls._parse_single_cell(tr)
            for tr in table.select("tr")[4:]
        ]

        header_data.extend(rows)
        res: List[List[Any]] = [list(column) for column in zip(*header_data)]
        header: List[str] = ['date', 'pair_number', 'discipline']
        data: List[Dict[str, Any]] =  [
            dict(zip(header, i[:len(header)]), **item)
            for i in res[1:]
            for item in i[len(header) + 2:]
        ]
        for item in data:
            item['date'] = datetime.datetime.strptime(item['date'].split(',')[0], "%d.%m.%Y").date()
        return data