from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

HTMLFile = open("Единое окно доступа.html", "r")
index = HTMLFile.read()

soup = BeautifulSoup(index, 'lxml')
error_div = soup.find(id="error_msg")

if error_div and "Неверный логин-пароль" in error_div.get_text():
    print(23)
# Print the parsed result
print(error_div)
