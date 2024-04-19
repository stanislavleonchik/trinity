import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import pdfplumber
import re


def read_pdf_o(pdf_path):
    res = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            res += page.extract_text()

    res = re.sub(r'-\n', '', res)
    res = re.sub(r'\n', ' ', res)
    res = re.sub(r'\[[^]]{1,65}]', '', res)
    res = re.sub(r'\d+', '', res)
    res = re.sub(r'\b(?=\w*[^a-zA-Z\W]\w*)(?![a-zA-Z]+\b)\w+', '', res)
    with open('debug/debug_text_from_pdf.txt', 'w') as f:
        f.write(res)

    return res


# https://stackoverflow.com/questions/53577162/extract-text-from-pdf-with-pypdf2
def read_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    res = ""
    for page_number in range(len(doc)):
        page = doc.load_page(page_number)
        pix = page.get_pixmap()
        img = Image.open(io.BytesIO(pix.tobytes()))

        text = pytesseract.image_to_string(img, lang='eng')

        res += text

    res = re.sub(r'-\n', '', res)
    res = re.sub(r'\n', ' ', res)
    res = re.sub(r'\[[^]]{1,65}]', '', res)
    res = re.sub(r'\([^)]{1,65}\)', '', res)
    res = re.sub(r'\d+', '', res)
    res = re.sub(r'\b(?=\w*[^a-zA-Z\W]\w*)(?![a-zA-Z]+\b)\w+', '', res)
    res = re.sub(r'\s+', ' ', res)
    res = re.sub(r'[|!?&…,"\'\\`]', '', res)

    with open('debug/debug_text_from_pdf.txt', 'w') as f:
        f.write(res)
    # Закрытие документа
    doc.close()
    return res
