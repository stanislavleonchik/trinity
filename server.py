import json
import spacy
from page import *
from flask import Flask, request, jsonify
from collocations import get_collocations
from tenses import search_batches_active_voice

app = Flask(__name__)
is_data_ready = False
nlp = spacy.load("en_core_web_trf"); print("[spaCy]: The model has been successfully loaded")
nlp.add_pipe("merge_entities")
nlp.add_pipe("merge_noun_chunks")
data = ""


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
    return jsonify(search_batches_active_voice(nlp, data, tense)[0]), 200


def to_json(result):
    ready_verb = result[0]
    ready_verb_list_length = len(ready_verb)
    raw_verb = result[2]
    perhaps = result[3]
    result = '['
    for i in range(ready_verb_list_length):
        dict_to_result = {"ready_verb": ready_verb[i][len(ready_verb[i]) - 1],
                          "raw_verb": raw_verb[i][len(raw_verb[i]) - 1],
                          "perhaps": perhaps[i]}
        result += json.dumps(dict_to_result)
        if i != ready_verb_list_length - 1:
            result += ', '
        else:
            result += ']'
    return result


if __name__ == '__main__':
    app.debug = True
    app.run(host='127.0.0.1', port=5000)
