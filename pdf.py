import fitz
import pytesseract
from PIL import Image
import io
import pdfplumber
import re
import nltk
from nltk import find
import unicodedata
import contractions
import inflect
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

packages = {
    "words": "corpora/words",
    "stopwords": "corpora/stopwords",
    "punkt": "tokenizers/punkt"
}

# Проверка наличия каждого пакета
for package, path in packages.items():
    try:
        find(path)
        print(f"Package '{package}' is already installed.")
    except LookupError:
        print(f"Package '{package}' not found, downloading...")
        nltk.download(package)


def read_pdf(pdf_path):
    res = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            res += page.extract_text()

    with open('debug/raw_pdf.txt', 'w') as f:
        f.write(res)

    res = re.sub('<[^<]+?>', '', res)  # HTML
    res = re.sub(r'-\n', '', res)
    res = re.sub(r'\n', ' ', res)
    res = re.sub(r'http\S+', '', res)  # URL
    # res = res.lower()
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
    with open('debug/pdf.txt', 'w') as f:
        f.write(res)

    return res
