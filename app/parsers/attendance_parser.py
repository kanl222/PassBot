from typing import Any, List, Dict, Optional
from aiohttp import ClientResponse
from bs4 import BeautifulSoup, Tag


class AttendanceParser:
    @staticmethod
    def _extract_status_from_class(class_names: tuple) -> str:
        """
        Efficiently map CSS classes to attendance status.
        
        Args:
            class_names: Tuple of CSS class names
        
        Returns:
            Attendance status string
        """
        class_mapping = {
            'cl-gray': 'absent',
            'cl-grn': 'present',
            'cl-or': 'late',
            'cl-red': 'violation',
            'cl-wh': 'unknown',
        }
        
        return next(
            (class_mapping[cls] for cls in class_names if cls in class_mapping),
            'unknown'
        )

    @classmethod
    def _parse_multiline_rows_state(cls, multiline_div) -> List[Dict[str, str]]:
        """Parse nested attendance details in multiline rows."""
        return [
            {
                'status': cls._extract_status_from_class(tuple(row.get('class', []))),
                'details': row.get('title', '').strip()
            }
            for row in multiline_div.findall(".//div[@class='multiline-rows-state']")
        ]

    @classmethod
    def _parse_single_cell(cls, cell) -> List[Dict[str, str]]:
        """Parse a single attendance cell."""
        multiline_container = cell.find(".//div[@class='multi_visit_container']")
        
        if multiline_container is not None:
            return cls._parse_multiline_rows_state(multiline_container)
        
        return [{
            'status': cls._extract_status_from_class(tuple(cell.get('class', []))),
            'details': cell.get('title', '').strip().split('\n')[-1]
        }]

    @classmethod
    async def parse_attendance(cls, html_content:str) -> List[Dict[str, Any]]:
        """
        Parse attendance information from HTML content asynchronously.

        Args:
            html_content: HTML string containing attendance table.

        Returns:
            List of dictionaries with student attendance data.
        """
        soup = BeautifulSoup(html_content, 'lxml')
        table = soup.find('table', {"class": "table-visits"})

        if not table:
            raise ValueError("No attendance table found in HTML")

        attendance_data = []
        rows = table.find_all('tr')[4:]  # Skip header rows

        for row in rows:
            cells = row.find_all('td')
            if len(cells) <= 2:
                continue

            student_name = cells[1].get_text(strip=True)

            classes = []
            for cell in cells[3:]:
                classes.extend(cls._parse_single_cell(cell))  # Flatten the structure

            attendance_data.append({
                'name': student_name,
                'attendance': classes
            })

        return attendance_data
