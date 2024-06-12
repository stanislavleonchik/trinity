import requests
from bs4 import BeautifulSoup
from readability import Document
from pdf import clean


def get_data_from_url(url='https://en.wikipedia.org/wiki/Artificial_intelligence'):
    response = requests.get(url)
    html_content = response.text

    doc = Document(html_content)
    readable_article_html = doc.summary()
    soup = BeautifulSoup(readable_article_html, 'html.parser')
    for a in soup.find_all('a'):
        a.replace_with(a.text)
    for element in soup(['img', 'figure', 'script', 'style']):
        element.decompose()
    res = soup.get_text(separator=' ', strip=True)
    with open('debug/raw_page.txt', 'w') as f:
        f.write(res)

    res = clean(res)

    return res
