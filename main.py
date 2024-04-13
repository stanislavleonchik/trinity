from flask import Flask, request, jsonify
import spacy as sp
import en_core_web_sm
from parser import *
import json

app = Flask(__name__)
nlp = sp.load("en_core_web_sm")
nlp.add_pipe("merge_entities")
nlp.add_pipe("merge_noun_chunks")
print(search_batches_active_voice(nlp, input(), 'PAST_SIMPLE'))


def to_json(result):
    ready_verb = result[0]
    ready_verb_list_lenght = len(ready_verb)
    raw_verb = result[2]
    perhaps = result[3]
    result = '['
    for i in range(ready_verb_list_lenght):
        dict_to_result = {}
        dict_to_result["ready_verb"] = ready_verb[i][len(ready_verb[i])-1]
        dict_to_result["raw_verb"] = raw_verb[i][len(raw_verb[i])-1]
        dict_to_result["perhaps"] = perhaps[i]
        result += json.dumps(dict_to_result)
        if i != ready_verb_list_lenght - 1:
            result += ', '
        else:
            result += ']'
    return result


@app.route('/')
@app.route('/get-text', methods=["POST"])
def index():
    jsn = request.get_json()
    print(jsn, '\n')
    text = clean_text(jsn['text'])
    print(text)
    res = search_batches_active_voice(nlp, text, 'PAST_SIMPLE')
    print(res[0])
    print(res[2])
    print(res[3])
    return jsonify(jsn)



if __name__ == '__main__':
    app.debug = True
    app.run(host='127.0.0.1', port=5000)


# @app.route('/get-test')
# def test_sender():
#     return to_json(res)
