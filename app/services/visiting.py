


import datetime

from app.services.users import get_all_teachers
from app.session.session_manager import SessionManager


async def pars_visiting(start_date=None, end_date=None):
    if start_date is None and end_date is None :
        start_date = datetime.now()
        end_date = start_date.now()
        
    teachers = await get_all_teachers()
    
    for teacher in teachers:
        login_password = teacher.get_encrypted_data()
        async with SessionManager(login_password['login'], login_password['password']) as sm:
            