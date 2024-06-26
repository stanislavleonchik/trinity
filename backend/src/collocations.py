from collections import Counter
from utils import process_text


def get_collocations(nlp, data_collocations):
    data_collocations = process_text(nlp, data_collocations)
    doc = nlp(data_collocations)
    collocations = []
    for token in doc:
        if token.is_alpha:
            if token.head.is_alpha:
                # Существительное + прилагательное + существительное
                if token.pos_ == 'NOUN' and token.head.pos_ == 'ADJ' and token.head.head.pos_ == 'NOUN':
                    collocations.append(f"{token.head.head.text.capitalize()} {token.head.text} {token.text}")
                    if token.dep_ in ('pobj', 'dobj', 'nsubj'):
                        adj1 = None
                        adj2 = None
                        noun1 = None

                        if token.head.pos_ == 'ADJ':
                            adj1 = token.head
                            if adj1.head.pos_ == 'ADJ':
                                adj2 = adj1.head
                                if adj2.head.pos_ == 'NOUN':
                                    noun1 = adj2.head
                                    if noun1.head.pos_ == 'NOUN':
                                        phrase = f"{adj2.text} {adj1.text} {noun1.text} {token.text}"
                                        collocations.append(phrase.capitalize())

                # Наречие + прилагательное
                if token.pos_ == 'ADV' and token.head.pos_ == 'ADJ' and len(token.head) > 2:
                    collocations.append(f"{token.text.capitalize()} {token.head.text}")

                # Прилагательное + существительное
                if token.pos_ == 'ADJ' and '-' not in token.text and token.dep_ == 'amod' and token.head.pos_ == 'NOUN':
                    collocations.append(f"{token.text.capitalize()} {token.head.text}")

            # Существительное + of + герундий
            if token.pos_ == 'NOUN' and token.n_rights == 1:
                for right in token.rights:
                    if right.dep_ == 'prep' and right.text == 'of':
                        for child in right.children:
                            if child.dep_ == 'pcomp' and child.tag_ == 'VBG':
                                collocations.append(f"{token.text.capitalize()} {right.text} {child.text}")

            # Прилагательное + прилагательное + ... + существительное
            if token.pos_ == 'NOUN' and token.n_lefts > 0:
                adjs = [child for child in token.lefts if child.pos_ == 'ADJ' and child.is_alpha]
                if len(adjs) > 1:
                    collocations.append(f"{" ".join([adj.text for adj in adjs])} {token.text}".capitalize())

            # Глагол с прямым дополнением
            if token.pos_ == 'VERB' and token.n_rights > 0:
                for right in token.rights:
                    if right.dep_ in ['dobj', 'obj'] and '-' not in right.text and right.is_alpha and len(right) > 2:
                        collocations.append(f"{token.text.capitalize()} {right.text}")

    collocations_three_words = [phrase for phrase in collocations if len(phrase.split()) == 3]

    collocations_other = [phrase for phrase in collocations if len(phrase.split()) != 3]

    filtered_collocations = collocations_three_words + collocations_other

    counts = Counter(filtered_collocations)

    colocs = []
    count = []
    for phrase in filtered_collocations:
        if phrase not in colocs:
            colocs.append(phrase)
            count.append(counts[phrase])
    return colocs, count
