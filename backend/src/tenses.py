import re
MODALS = ["must", "can", "should", "could", "may", "might"]


def get_active_tense_rule(tense):
    tense_list = {
        "PRESENT_SIMPLE": dict(aux=[], vtag=["VBZ", "VBP"]),
        "PRESENT_CONTINUOUS": dict(aux=["am", "is", "are"], vtag=["VBG"]),
        "PRESENT_PERFECT": dict(aux=["has", "have"], vtag=["VBN"]),
        "PRESENT_PERFECT_CONTINUOUS": dict(aux=["has", "have"], vtag=["VBN", "VBG"]),

        "PAST_SIMPLE": dict(aux=["did"], vtag=["VBD"]),
        "PAST_CONTINUOUS": dict(aux=["was", "were"], vtag=["VBG"]),
        "PAST_PERFECT": dict(aux=["had"], vtag=["VBN"]),
        "PAST_PERFECT_CONTINUOUS": dict(aux=["had"], vtag=["VBN", "VBG"]),

        "FUTURE_SIMPLE": dict(aux=["will"], vtag=["VB"]),
        "FUTURE_CONTINUOUS": dict(aux=["will be"], vtag=["VBG"]),
        "FUTURE_PERFECT": dict(aux=["will have"], vtag=["VBN"]),
        "FUTURE_PERFECT_CONTINUOUS": dict(aux=["will have been"], vtag=["VBN", "VBG"]),

        "ALL": dict(aux=["do", "does", "did", "am", "is", "are", "has", "have", "was", "were", "had", "will", "would", "should", "shall", "be"], vtag=["VB", "VBZ", "VBP", "VBG", "VBN", "VBD"])
    }
    return tense_list.get(tense, tense_list["ALL"])


def search_batches_indexes(text, batch_size):
    exp = r'[.?!](?= [A-Z]|$)'
    cur_index = 0
    batch_indexes = [0]

    while cur_index < len(text):
        find_start = cur_index
        find_end = cur_index + batch_size

        if find_end > len(text):
            find_end = len(text)

        match = re.search(exp, text[find_start:find_end])
        if match:
            cur_index = match.end() + find_start
            batch_indexes.append(cur_index)
        else:
            cur_index = find_end

    return batch_indexes


def search_batches_active_voice(nlp, text, grammar_rule='ALL'):
    # Добавляем пайплайны для объединения сущностей и именованных групп
    nlp.add_pipe("merge_entities")
    nlp.add_pipe("merge_noun_chunks")

    # Разделение текста на батчи по 5000 символов
    batch_indexes = search_batches_indexes(text, 5000)
    text_split = [text[batch_indexes[i - 1]:batch_indexes[i]] for i in range(1, len(batch_indexes))]

    # Обработка батчей с помощью spaCy
    docs = list(nlp.pipe(text_split))

    # Получение правила для активного залога в зависимости от грамматического правила
    tense_rule = get_active_tense_rule(grammar_rule)

    # Инициализация списков для хранения результатов
    active_phrases = []
    active_phrases_lexemes = []
    active_phrases_indexes = []
    active_phrases_sent = []
    active_phrases_pos = []
    active_phrases_dep = []

    # Проход по каждому батчу
    for currentBatch, doc in enumerate(docs):
        # Проход по каждому предложению в батче
        for sent in doc.sents:
            # Проход по каждому токену в предложении
            for token in sent:
                # Если тег токена соответствует правилам активного залога
                if token.tag_ in tense_rule.get('vtag'):
                    # Инициализация временных списков для хранения текущего совпадения
                    active_match = []
                    active_match_indexes = []
                    active_match_lexemes = []
                    active_match_pos = []
                    active_match_dep = []

                    to_inf_match = []
                    subject_found = False
                    prt_contained = False

                    # Проход по детям текущего токена
                    for child in token.children:
                        child_lower = child.text.lower()
                        if child.dep_ == 'nsubj':
                            # Если ребенок - подлежащее, добавляем его в список активных совпадений
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
                            # Если ребенок - пассивный вспомогательный глагол, обнуляем текущие совпадения
                            active_match = []
                            active_match_indexes = []
                            active_match_lexemes = []
                            active_match_pos = []
                            active_match_dep = []
                            break

                        if child.dep_ == 'aux':
                            # Если ребенок - вспомогательный глагол, проверяем его соответствие правилам
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
                            # Если ребенок - зависимое дополнение, добавляем его в список инфинитивных совпадений
                            for grandchild in child.children:
                                if grandchild.dep_ == 'aux':
                                    to_inf_match.append(grandchild)

                            to_inf_match.append(child)

                        if child.dep_ == 'neg':
                            # Если ребенок - отрицание, добавляем его в активные совпадения
                            active_match.append(child.text)
                            active_match_lexemes.append(child.lemma_)
                            active_match_indexes.append([child.idx - sent.start_char,
                                                         child.idx + len(child) - sent.start_char])
                            active_match_pos.append(child.pos_)
                            active_match_dep.append(child.dep_)
                        if child.dep_ == 'prt':
                            # Если ребенок - частица, добавляем её и токен в активные совпадения
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

                    # Если активные совпадения найдены и найдено подлежащее
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

    # Формирование результирующего списка
    result = [active_phrases, active_phrases_indexes, active_phrases_lexemes,
              active_phrases_sent, active_phrases_pos, active_phrases_dep]

    # Удаление добавленных пайплайнов
    nlp.remove_pipe("merge_entities")
    nlp.remove_pipe("merge_noun_chunks")

    return result
