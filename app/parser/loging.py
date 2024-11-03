from requests import post,Session



payload = {
    'login': 'kanl222fdd@gmail.com',
    'pwd': 'hKJ-8Qk-4St-gna',
}
import requests
from requests.auth import HTTPBasicAuth


with Session() as sess:
    sess.auth = ('kanl222fdd@gmail.com','hKJ-8Qk-4St-gna')
    sess.auth
    pt = sess.post('https://www.osu.ru/iss/1win/',data=payload)
    print(pt.status_code)
    print(pt.cookies.values())
    print(pt.text)