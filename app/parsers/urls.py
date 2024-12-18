"""
Module with URL templates for accessing various resources on the platform.
"""

# Base URLs
BASE_PREPOD_URL = "https://www.osu.ru/iss/prepod/lk.php"
BASE_STUDENT_URL = "https://www.osu.ru/iss/lks/"
BASE_URL = "https://www.osu.ru/iss/1win/"
LOGOUT_URL = f'{BASE_URL}?page=logout'
# Specific page URLs for students
link_to_login = BASE_URL  # Login page
link_to_progress = f"{BASE_STUDENT_URL}?page=progress"  # Student progress page
link_to_supervision = f"{BASE_STUDENT_URL}?page=supervision"  # Supervision page
link_to_profile = f"{BASE_STUDENT_URL}?page=profile"  # Profile page
link_to_personal = f"{BASE_STUDENT_URL}?page=personal"  # Personal info page
link_to_unlogin = f"{BASE_STUDENT_URL}?page=logout"  # Logout page

# Specific page URLs for teachers
link_teacher_progress = f"{BASE_PREPOD_URL}?page=progress"  # Teacher progress page
link_teacher_supervision = f"{BASE_PREPOD_URL}?page=supervision"  # Supervision page
link_teacher_profile = f"{BASE_PREPOD_URL}?page=profile"  # Profile page
link_teacher_personal = f"{BASE_PREPOD_URL}?page=personal"  # Personal info page
link_teacher_unlogin = f"{BASE_PREPOD_URL}?page=logout"  # Logout page

# Links with dynamic parameters for teachers
link_to_list_group_students = (
    f"{BASE_PREPOD_URL}?page=students&amp;group={{id_group}}"  # Student group page
)
link_to_activity = (
    f"{BASE_PREPOD_URL}?page=supervision&amp;view=visits&amp;group={{id_group}}"  # Activity tracking page
)

# List of exported URLs
__all__: list[str] = [
    # Student URLs
    "link_to_supervision",
    "link_to_login",
    "link_to_profile",
    "link_to_personal",
    "link_to_unlogin",
    "link_to_progress",
    
    # Teacher URLs
    "link_teacher_progress",
    "link_teacher_supervision",
    "link_teacher_profile",
    "link_teacher_personal",
    "link_teacher_unlogin",
    "link_to_list_group_students",
    "link_to_activity",
]
