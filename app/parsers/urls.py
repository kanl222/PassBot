"""
Module with URL templates for accessing various resources on the platform.
"""
from click.core import batch

# Base URLs
BASE_URL = "https://www.osu.ru/iss/prepod/lk.php"

# Specific page URLs
link_to_login = "https://www.osu.ru/iss/1win/"
link_to_supervision = f"{BASE_URL}?page=supervision"
link_to_profile = f"{BASE_URL}?page=profile"
link_to_progress = f"https://www.osu.ru/iss/lks/?page=progress"
link_to_personal = f"{BASE_URL}?page=personal"
link_to_unlogin = f"{BASE_URL}page=unlogin"
link_to_list_group_students = f"{BASE_URL}?page=students&amp;group={{id_group}}"
link_to_activity = f"{BASE_URL}?page=supervision&amp;view=visits&amp;group={{id_group}}"

__all__ = [
    "link_to_supervision",
    "link_to_login",
    "link_to_profile",
    "link_to_list_group_students",
    "link_to_activity"
]
