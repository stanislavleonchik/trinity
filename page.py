import requests
from readability import Document
from bs4 import BeautifulSoup
from parser import clean_text


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
    text = soup.get_text(separator=' ', strip=True)
    text = ' '.join(text.split())
    text = clean_text(text)

    return text
