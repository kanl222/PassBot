from requests import post,Session
from selenium import webdriver



data = {
    'login': 324234,
    'psw': 3432424,
}

form = """<form action="https://www.osu.ru/iss/prepod/lk.php" method="post">
    <input style="display:none" type="text" name="_login">
    <input style="display:none" type="asdpassword" id="_password" name="_password" value="********">
    <table class="wide" style="">
    <tbody><tr height="50%"><td colspan="2" class="nb_center_bottom"></td></tr>
    <tr><td class="nb_right"><span class="f10">Логин</span></td><td class="nb_left"><input class="login" name="login" type="text" value=""></td></tr>
    <tr><td class="nb_right"><span class="f10">Пароль</span></td><td class="nb_left"><input class="login" id="opsw" name="opsw" type="password"></td></tr>
    <tr height="50%"><td class="nb"></td><td class="nb_left_top"><input class="button" type="submit" value="Подключиться" onclick="SetPassword()"></td></tr>
    </tbody></table>
    <input type="hidden" id="psw" name="psw" value="">
    
    </form>"""



with Session() as sess:
    pt = sess.post('https://www.osu.ru/iss/prepod/lk.php?',data=data)
    print(pt.cookies.values())
    print(pt.text)