import os
import json
import spacy
from page import *
from flask import Flask, request, jsonify
from collocations import get_collocations
from pdf import read_pdf
from tenses import search_batches_active_voice

app = Flask(__name__)
data, is_data_ready = None, False
nlp = spacy.load("en_core_web_trf"); print("[spaCy]: The model has been successfully loaded")



@app.route('/web', methods=["GET"])
def web():
    global data, is_data_ready
    data = get_data_from_url(request.args.get('url'))
    if data == -1:
        return "Bad url", 400
    is_data_ready = True
    return "Got url", 200


@app.route('/collocations', methods=["GET"])
def collocations():
    if not is_data_ready:
        return "Data is not ready yet", 200
    return jsonify(get_collocations(nlp, data)), 200


@app.route('/tense', methods=["GET"])
def tenses():
    if not is_data_ready:
        return "Data is not ready yet", 200
    tense = request.args.get('tense')
    return jsonify(to_json(search_batches_active_voice(nlp, data, tense))), 200


@app.route('/upload-pdf', methods=["POST"])
def upload_pdf():
    os.makedirs("./documents", exist_ok=True)
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    if file and file.filename.endswith('.pdf'):
        directory = os.path.join(app.root_path, 'documents')
        if not os.path.exists(directory):
            os.makedirs(directory)
        filepath = os.path.join(directory, file.filename)
        file.save(filepath)
        global data, is_data_ready
        data = read_pdf(filepath)
        is_data_ready = True
        return f"File \"{file.filename}\" saved", 200
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
    app.run(host='127.0.0.1', port=5000)
