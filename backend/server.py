import time

import spacy
from page import *
from flask import Flask, request, jsonify
from collocations import get_collocations
from pdf import *
from translate import *
from tenses import search_batches_active_voice
from flask import Flask

from utils import calculate_hash

app = Flask(__name__)
directory_documents = os.path.join(app.root_path, 'documents')
directory_cash_pdf_texts = os.path.join(app.root_path, 'cash-pdf-texts')
directory_cash_terms = os.path.join(app.root_path, 'cash-terms')
cash = os.path.join(app.root_path, 'cash')
if not os.path.exists(cash):
    os.makedirs(cash)
if not os.path.exists(directory_documents):
    os.makedirs(directory_documents)
if not os.path.exists(directory_cash_pdf_texts):
    os.makedirs(directory_cash_pdf_texts)
if not os.path.exists(directory_cash_terms):
    os.makedirs(directory_cash_terms)
is_data_pdf_ready = False
nlp = spacy.load("en_core_web_trf"); print("[spaCy]: The model has been successfully loaded")
os.makedirs("./debug", exist_ok=True)


@app.route('/web', methods=["GET"])
def web():
    global data_pdf, is_data_pdf_ready
    url = request.args.get('url')
    if data_pdf:
        data_pdf = get_data_from_url(url)
        return jsonify({"message": "URL has been successfully received", "article_link": url}), 200
    else:
        return jsonify({"error": "No article link provided"}), 400


@app.route('/collocations', methods=["GET"])
def collocations():
    file_hash = request.headers.get('hash')
    print(file_hash)
    if file_hash not in os.listdir(directory_cash_pdf_texts):
        return jsonify("File not found"), 200

    if not is_data_pdf_ready:
        return jsonify("Data is not ready yet"), 200

    if file_hash not in os.listdir(directory_cash_terms):
        with open(os.path.join(directory_cash_pdf_texts, file_hash), 'r') as f:
            text = f.read()
        colocs, counts = get_collocations(nlp, text)
        translations = load_dictionary()
        to_translate = []
        for coloc in colocs:
            if coloc not in translations:
                to_translate.append(coloc)
        if len(to_translate) > 0:
            v2_json = []
            for bound in calculate_bounds(to_translate):
                v2_json.extend(translate_collocations(to_translate[bound[0]:bound[1]]))
            v2_json.reverse()
            for coloc in colocs:
                if coloc not in translations:
                    translations[coloc] = v2_json.pop()

        save_dictionary(translations)
        res = [{'coloc': coloc, 'count': counts[i], 'translation': translations[coloc]} for i, coloc in enumerate(colocs)]
        with open(os.path.join(directory_cash_terms, file_hash), 'w') as f:
            f.write(json.dumps(res))

        return jsonify(res), 200
    else:
        with open(os.path.join(directory_cash_terms, file_hash), 'r') as f:
            time.sleep(2)
            return jsonify(json.loads(f.read())), 200  # f.read(), 200


@app.route('/tense', methods=["GET"])
def tenses():
    if not is_data_pdf_ready:
        return "Data is not ready yet", 200
    tense = request.args.get('tense')
    res = search_batches_active_voice(nlp, data_pdf, tense)
    for i, (gb, sent) in enumerate(zip(res[0], res[3])):
        res[3][i] = res[3][i].replace(gb[1], '_'*len(gb[1]))
    return jsonify(to_json(res)), 200


@app.route('/upload-pdf', methods=["POST"])
def upload_pdf():
    global is_data_pdf_ready
    client_id = request.headers.get('X-Client-ID')

    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    if file and file.filename.endswith('.pdf'):
        filepath = os.path.join(directory_documents, file.filename)
        file.save(filepath)

        hash_file = calculate_hash(filepath)
        if hash_file not in os.listdir(directory_cash_pdf_texts):
            with open(os.path.join(directory_cash_pdf_texts, hash_file), 'w') as f:
                f.write(read_pdf(filepath))

        is_data_pdf_ready = True
        return jsonify({"message": f"File \"{file.filename}\" saved", "hash": hash_file}), 200
    else:
        return "Invalid file format", 400


def to_json(result):
    ready_verb = result[0]
    ready_verb_list_length = len(ready_verb)
    raw_verb = result[2]
    sentence = result[3]
    result = []
    for i in range(ready_verb_list_length):
        dict_to_result = {"ready_verb": ready_verb[i][len(ready_verb[i]) - 1],
                          "raw_verb": raw_verb[i][len(raw_verb[i]) - 1],
                          "sentence": sentence[i]}
        result.append(dict_to_result)

    return result


if __name__ == '__main__':
    app.debug = True
    app.run(host='192.168.0.97', port=8090)
