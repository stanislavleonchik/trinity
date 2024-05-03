import os
import re
from spacy.lang.en.stop_words import STOP_WORDS


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
