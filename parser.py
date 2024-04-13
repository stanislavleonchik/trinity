import os
import re

MODALS = ["must", "can", "should", "could", "may", "might"]


def clean_text(text):
    # text = re.split(r'[.!?\n]', text)
    split_regex = re.compile(r'[|!|?|&…]')
    text = filter(lambda t: t, [t.strip() for t in split_regex.split(text)])
    text = ' .'.join(text)
    text = os.linesep.join([s for s in text.splitlines() if s])
    text = hyphens(text)
    text = fancy_dot(text)
    return text


def fancy_dot(text):
    return text.replace(u"\u1427", ".")


def hyphens(text):
    replace_list = [
        u"\u002d", u"\u058a", u"\u058b", u"\u2010", u"\u2010", u"\u2012", u"\u2013",
        u"\u2014", u"\u2015", u"\u2e3a", u"\u2e3b", u"\ufe58", u"\ufe63", u"\uff0d",
    ]
    for item in replace_list:
        text = text.replace(item, "-")
    return text


def get_active_tense_rule(tense):
    tense_list = {
        "PAST_SIMPLE":
            dict(aux=["did"], vtag=["VBD"]),
        "ALL": dict(aux=["do", "does", "did", "am", "is", "are", "have", "has", "was", "were", "had", "shall", "will", "would", "should", "be"],
                    vtag=["VB", "VBZ", "VBP", "VBG", "VBN", "VBD"])
    }
    return tense_list.get(tense, "ALL")


def search_batches_indexes(text, batch_size):
    exp = r'[.?!](?= [A-Z]|$)'
    cur_index = 0
    find_start = 0
    batch_indixes = [0]
    sentence_found = False

    while find_start < len(text):
        find_start = cur_index + batch_size
        find_end = find_start + batch_size

        # Check if the right index is less or equal to the length of the text.
        if find_end > len(text):
            find_end = len(text)

        # Use Regex to find the end of a sentence in a text span.
        match = re.search(exp, text[find_start:find_end])
        # If a match is found, recalculate the indices and add to the list.
        if match:
            cur_index = match.end() + find_start - 1
            batch_indixes.append(cur_index)
            sentence_found = True
        else:
            # Just shift the index otherwise.
            cur_index += batch_size
            sentence_found = False

    # Add the last index if there is significant text at the end of the raw text.
    if sentence_found:
        batch_indixes.append(len(text))

    return batch_indixes


def search_batches_active_voice(nlp, text, grammar_rule='ALL'):
    text = clean_text(text)
    batch_indexes = search_batches_indexes(text, 5000)
    text_split = [text[batch_indexes[i - 1]:batch_indexes[i]] for i in range(1, len(batch_indexes))]

    docs = list(nlp.pipe(text_split))
    print(list(nlp.pipe(text_split)))

    tense_rule = get_active_tense_rule(grammar_rule)

    active_phrases = []
    active_phrases_lexemes = []
    active_phrases_indexes = []
    active_phrases_sent = []
    active_phrases_pos = []
    active_phrases_dep = []

    for currentBatch, doc in enumerate(docs):
        for sent in doc.sents:
            for token in sent:
                if token.tag_ in tense_rule.get('vtag'):
                    active_match = []
                    active_match_indexes = []
                    active_match_lexemes = []
                    active_match_pos = []
                    active_match_dep = []

                    to_inf_match = []
                    subject_found = False
                    prt_contained = False

                    for child in token.children:
                        child_lower = child.text.lower()
                        if child.dep_ == 'nsubj':
                            active_match.append(child.text)
                            if child.lemma_ == "-PRON-":
                                active_match_lexemes.append(child.text)
                            else:
                                active_match_lexemes.append(child.lemma_)
                            active_match_indexes.append([child.idx - sent.start_char,
                                                       child.idx + len(child) - sent.start_char])
                            active_match_pos.append(child.pos_)
                            active_match_dep.append(child.dep_)
                            subject_found = True

                        if child.dep_ == 'auxpass':
                            active_match = []
                            active_match_indexes = []
                            active_match_lexemes = []
                            active_match_pos = []
                            active_match_dep = []
                            break

                        if child.dep_ == 'aux':
                            if child_lower in tense_rule.get('aux') or child_lower in MODALS:
                                active_match.append(child.text)
                                active_match_lexemes.append(child.lemma_)
                                active_match_indexes.append([child.idx - sent.start_char,
                                                           child.idx + len(child) - sent.start_char])
                                active_match_pos.append(child.pos_)
                                active_match_dep.append(child.dep_)
                            else:
                                active_match = []
                                active_match_lexemes = []
                                active_match_indexes = []
                                active_match_pos = []
                                active_match_dep = []
                                break

                        if child.dep_ == 'xcomp':
                            for grandchild in child.children:
                                if grandchild.dep_ == 'aux':
                                    to_inf_match.append(grandchild)

                            to_inf_match.append(child)

                        if child.dep_ == 'neg':
                            active_match.append(child.text)
                            active_match_lexemes.append(child.lemma_)
                            active_match_indexes.append([child.idx - sent.start_char,
                                                       child.idx + len(child) - sent.start_char])
                            active_match_pos.append(child.pos_)
                            active_match_dep.append(child.dep_)
                        if child.dep_ == 'prt':
                            active_match.append(token.text)
                            active_match.append(child.text)

                            active_match_lexemes.append(token.lemma_)
                            active_match_lexemes.append(child.lemma_)

                            active_match_indexes.append([token.idx - sent.start_char,
                                                       token.idx + len(token) - sent.start_char])
                            active_match_indexes.append([child.idx - sent.start_char,
                                                       child.idx + len(child) - sent.start_char])

                            active_match_pos.append(token.pos_)
                            active_match_pos.append(child.pos_)

                            active_match_dep.append(token.dep_)
                            active_match_dep.append(child.dep_)

                            prt_contained = True
                    if active_match and subject_found:
                        if not prt_contained:
                            active_match.append(token.text)
                            active_match_lexemes.append(token.lemma_)
                            active_match_indexes.append([token.idx - sent.start_char,
                                                       token.idx + len(token) - sent.start_char])
                            active_match_pos.append(token.pos_)
                            active_match_dep.append(token.dep_)

                        if to_inf_match:
                            [active_match.append(t.text) for t in to_inf_match]
                            [active_match_lexemes.append(t.lemma_) for t in to_inf_match]
                            [active_match_indexes.append([t.idx - sent.start_char,
                                                        t.idx + len(t) - sent.start_char]) for t in to_inf_match]
                            [active_match_pos.append(t.pos_) for t in to_inf_match]
                            [active_match_dep.append(t.dep_) for t in to_inf_match]

                        batch_idx = batch_indexes[currentBatch]
                        active_phrases.append(active_match)
                        active_phrases_lexemes.append(active_match_lexemes)
                        active_phrases_indexes.append(active_match_indexes)
                        active_phrases_sent.append(text[batch_idx + sent.start_char:batch_idx + sent.end_char].strip())
                        active_phrases_pos.append(active_match_pos)
                        active_phrases_dep.append(active_match_dep)
                        pass

        result = [active_phrases, active_phrases_indexes, active_phrases_lexemes,
                  active_phrases_sent, active_phrases_pos, active_phrases_dep]

        return result
