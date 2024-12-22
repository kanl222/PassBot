from typing import Any, List, Dict, Optional
from bs4 import BeautifulSoup, NavigableString, Tag
import json

class VisitingParser:
    @staticmethod
    def _extract_attendance_status(cell: Tag) -> str:
        """Determine attendance status from cell's CSS classes."""
        div = cell.find('div', class_='visit-container')
        if not div:
            return 'unknown'
        
        class_mapping = {
            'cl-gray': 'absent',
            'cl-grn': 'present',
            'cl-wh': 'unknown'
        }
        
        cell_class = div.find('div')['class'][0]
        return class_mapping.get(cell_class, 'unknown')

    @classmethod
    def parse_attendance(cls, html_content: str) -> List[Dict[str, Any]]:
        """
        Parse attendance information from HTML content.
        
        Args:
            html_content: HTML string containing attendance table.
        
        Returns:
            List of dictionaries with student attendance data.
        """
        soup = BeautifulSoup(html_content, 'lxml')
        table: Tag | NavigableString | None = soup.find('table', {"class": "table-visits"})
        
        if not table:
            raise ValueError("No attendance table found in HTML")
        
        attendance_data = []
        rows = table.find_all('tr')[4:]  # Skip header rows
        
        for row in rows:
            cells = row.find_all('td')
            if len(cells) <= 2:
                continue
            
            student_name = cells[1].get_text(strip=True)
            classes = [
                {
                    'status': cls._extract_attendance_status(cell),
                    'details': cell.get('title', '')
                }
                for cell in cells[3:]
            ]
            
            attendance_data.append({
                'name': student_name,
                'attendance': classes
            })
        
        return attendance_data
