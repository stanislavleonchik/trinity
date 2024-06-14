import os
import re
import json
import nltk
import dotenv
import inflect
import hashlib
import requests
import wordninja
import pdfplumber
import unicodedata
import contractions
from nltk import find
from bs4 import BeautifulSoup
from readability import Document
from nltk.corpus import stopwords
from nltk.corpus import words as w
from nltk.tokenize import word_tokenize

packages = {
    "words": "corpora/words",
    "stopwords": "corpora/stopwords",
    "punkt": "tokenizers/punkt"
}

for package, path in packages.items():
    try:
        find(path)
        print(f"Package '{package}' is already installed.")
    except LookupError:
        print(f"Package '{package}' not found, downloading...")
        nltk.download(package)

def calculate_hash(file_path):
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


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

    res = clean(res)

    return res


def clean_text_o(text):
    split_regex = re.compile(r'[|!?&…]')
    dash_regex = re.compile(r'[\u002d\u058a\u058b\u2010\u2012\u2013\u2014\u2015\u2e3a\u2e3b\ufe58\ufe63\uff0d]')
    parts = [part.strip() for part in split_regex.split(text) if part.strip()]
    cleaned_text = ' .'.join(parts)
    cleaned_text = dash_regex.sub('', cleaned_text)
    cleaned_text = cleaned_text.replace(u"\u1427", ".")
    cleaned_text = os.linesep.join([s.strip() for s in cleaned_text.splitlines() if s.strip()])

    return cleaned_text


def get_noun_chunks(nlp, data):
    filtered_tokens = [token.lemma_ for token in nlp(data) if
                       token.is_alpha and not token.is_stop and token.text not in nlp.Defaults.stop_words and token.text not in {
                           'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
                           'October', 'November', 'December'}]

    return ' '.join(filtered_tokens)


def process_text(nlp, text):
    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 10]

    return ''.join(sentences)


def clean(res):
    res = re.sub('<[^<]+?>', '', res)
    res = re.sub(r'-\n', '', res)
    res = re.sub(r'\n', ' ', res)
    res = re.sub(r'http\S+', '', res)

    res = unicodedata.normalize('NFKD', res).encode('ascii', 'ignore').decode('utf-8', 'ignore')
    res = contractions.fix(res)
    res = re.sub(r'[^a-zA-Z0-9\s\.]', ' ', res)
    temp = inflect.engine()
    words = []
    for word in res.split():
        if word.isdigit():
            words.append(temp.number_to_words(word))
        else:
            words.append(word)
    res = ' '.join(words)
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(res)
    tokens = [token for token in tokens if token not in stop_words]
    res = ' '.join(tokens)
    res = re.sub(r'[^\w\s\.]', '', res)
    res = re.sub(r'\s\.', '.', res)
    res = re.sub(r'\.([^\.])', r'. \1', res)
    res = re.sub(r'\s+', ' ', res)
    existing_words = set(w.words())
    filtered_words = []
    for word in re.findall(r'\b\w{1,2}\b', res):
        if word in existing_words:
            filtered_words.append(word)
        else:
            filtered_words.append('')

    filtered_words_iter = iter(filtered_words)
    text = re.sub(r'\b\w{1,2}\b', lambda match: next(filtered_words_iter), res)
    text = text.replace('\n', ' ')

    text = re.sub(r'\s+', ' ', text)

    words = wordninja.split(text)

    split_text = ' '.join(words)

    return split_text

def read_pdf(pdf_path):
    res = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            res += page.extract_text()

    res = clean(res)

    return res


dotenv.load_dotenv()

API_KEY = os.getenv("API_KEY")
folder_id = os.getenv("FOLDER_ID")
source_language_code = 'en'
target_language = 'ru'
speller = 'true'


def translate_collocations(texts):
    body = {
        "sourceLanguageCode": source_language_code,
        "targetLanguageCode": target_language,
        "texts": texts,
        "folderId": folder_id,
        "speller": speller,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Api-Key {0}".format(API_KEY)
    }

    response = requests.post('https://translate.api.cloud.yandex.net/translate/v2/translate',
                             json=body,
                             headers=headers
                             )

    response_dict = response.json()

    if response.status_code == 200:
        return [coloc['text'] for coloc in response_dict.get('translations', [])]
    else:
        print(response.text)
        return []


def load_dictionary():
    try:
        with open("../translations.json", 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_dictionary(dictionary):
    with open("../translations.json", 'w', encoding='utf-8') as file:
        json.dump(dictionary, file, ensure_ascii=False, indent=4)


def calculate_bounds(words, limit=5000):
    lengths = [len(word) for word in words]
    bounds, current_sum, last_index = [], 0, 0

    for i, length in enumerate(lengths):
        if current_sum + length + (1 if current_sum else 0) > limit:
            bounds.append((last_index, i))
            last_index = i
            current_sum = length
        else:
            current_sum += length + (1 if current_sum else 0)

    if last_index < len(words):
        bounds.append((last_index, len(words)))

    return bounds
