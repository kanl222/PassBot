from bs4 import BeautifulSoup
from aiohttp import ClientResponse
from urllib.parse import urlparse
from urllib.parse import parse_qs


async def parse_groups(response: ClientResponse):
    """
    Function for parsing group data from HTML code.

    :param response: HTML code with a table of groups.
    :return None:.
     """
    soup = BeautifulSoup(await response.text(), 'lxml')
    rows = soup.find_all('tr')
    for row in rows:
        group_name_tag = row.find('td', class_='limit-width')
        if group_name_tag:
            group_name = group_name_tag.get_text(strip=True)
        group_link = row.find('a', href=True)['href']
        parsed_url = urlparse(group_link)
        group_id = parse_qs(parsed_url.query)['group_id'][0]


