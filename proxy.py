from urllib.parse import urlparse
from requests import Request, Session
import gzip
from lxml import html
from bs4 import BeautifulSoup, SoupStrainer


def application(environ, start_response):
    raw_uri = environ['RAW_URI']
    if not raw_uri.startswith('http'):
        raw_uri = 'https://habrahabr.ru' + raw_uri

    parsed_url = urlparse(raw_uri)
    parsed_url._replace(netloc='habrahabr.ru')
    url = parsed_url.geturl()

    print('url', url)

    method = environ['REQUEST_METHOD']

    headers = {}
    for key, value in environ.items():
        if not key.startswith('HTTP_'):
            continue
        headers[key[5:].replace('_', ' ').title().replace(' ', '-')] = value

    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError):
        request_body_size = 0
    request_body = environ['wsgi.input'].read(request_body_size)

    s = Session()

    req = Request(method, parsed_url.geturl(), headers=headers)
    prepped = req.prepare()
    prepped.body = request_body
    response = s.send(prepped)
    print('Вошло')
    content = html_update(response.text)
    print('Прошло')
    content = content.replace('https://habrahabr.ru/', 'http://localhost:8000/')
    content = content.replace('habrahabr.ru', 'localhost:8000')

    start_response("200 OK", response.headers.items())
    yield gzip.compress(content.encode('utf-8'))


def html_update(content):
    soup = BeautifulSoup(content, 'html.parser')
    str_soup = str(soup)
    for div in soup.findAll('div', {'class': 'post__text'}):
        words = div.get_text().split(' ')
        for word in words:
            word = str(word).replace(',', '').replace('.', '').replace(' ', '').replace(':', '')
            if len(word) == 6:
                print(word)
                str_soup = str_soup.replace(word, word + u'™')
    str_soup = str_soup.replace(u'™™', u'™').replace(u'™™™', u'™').replace(u'™™™™', u'™').replace(u'™™™™™', u'™')
    return str_soup