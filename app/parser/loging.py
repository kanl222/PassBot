from requests import post,Session



payload = {
    'login': 'kanl222fdd@gmail.com',
    'pwd': 'hKJ-8Qk-4St-gna',
}

form = """<form method="post" action="">
              <fieldset><label for="login" class="label">Мой логин:</label>
                <input type="text" id="login" name="login" value=""/>
                <label for="pass" class="label">Мой пароль:</label>
                <input type="password" id="pass"  name="pwd" autocomplete="off" value="" />
                <input type="submit" class="submit" value="Вход" />
              </fieldset>
            </form>"""
import requests
from requests.auth import HTTPBasicAuth


with Session() as sess:
    sess.auth = ('kanl222fdd@gmail.com','hKJ-8Qk-4St-gna')
    pt = sess.post('https://www.osu.ru/iss/1win/',data=payload)
    print(pt.status_code)
    print(pt.cookies.values())
    print(pt.text)