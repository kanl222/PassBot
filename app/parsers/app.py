from ..session.session_manager import get_user_session
from .urls import link_to_login
import logging
from .teacher_parser import parse_teacher
from . student_parser import parse_users
user_input_data = {
    'id_user_telegram': 32423423,  # Telegram ID пользователя, число
    'password': '324234',         # Пароль в открытом виде (будет обработан позже)
    'login': 'ekjojrow',          # Логин пользователя
    'entrance_status': 'prepod', # Статус или роль пользователя
}

async def authenticated_users(user_input_data: dict):
    """
    Authenticates a user based on provided credentials.

    Args:
        user_input_data (dict): Dictionary containing user credentials.

    Returns:
        dict: Result of the authentication, e.g., success or error details.
    """
    login = user_input_data['login']
    password = user_input_data['password']
    
    async with get_user_session(login, password) as sess:
        async with sess.post(
            link_to_login,
            data={
                'username': login,
                'password': password
            }
        ) as response:
            if response.status == 200:
                if user_input_data['entrance_status'] == 'prepod':
                    pass
                elif user_input_data['entrance_status'] == 'student':
                    pass
                
            else:
                error_details = await response.text()
                logging.error(error_details)
                
