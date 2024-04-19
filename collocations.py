from collections import Counter
from parser import *


def get_collocations(nlp, data_collocations):
    data_collocations = process_text(nlp, data_collocations)
    with open('debug/debug_text_before_collocations.txt', 'w') as f:
        f.write(data_collocations)
    doc = nlp(data_collocations)
    collocations = []
    for token in doc:
        if token.is_alpha:
            if token.head.is_alpha:
                # Существительное + прилагательное + существительное
                if token.pos_ == 'NOUN' and token.head.pos_ == 'ADJ' and token.head.head.pos_ == 'NOUN':
                    collocations.append(f"{token.head.head.text.capitalize()} {token.head.text} {token.text}")

                # Наречие + прилагательное
                elif token.pos_ == 'ADV' and token.head.pos_ == 'ADJ':
                    collocations.append(f"{token.text.capitalize()} {token.head.text}")

                # Прилагательное + существительное
                elif token.pos_ == 'ADJ' and '-' not in token.text and token.dep_ == 'amod' and token.head.pos_ == 'NOUN':
                    collocations.append(f"{token.text.capitalize()} {token.head.text}")

            # Существительное + of + герундий
            if token.pos_ == 'NOUN' and token.n_rights == 1:
                for right in token.rights:
                    if right.dep_ == 'prep' and right.text == 'of':
                        for child in right.children:
                            if child.dep_ == 'pcomp' and child.tag_ == 'VBG':
                                collocations.append(f"{token.text.capitalize()} {right.text} {child.text}")

            # Прилагательное + прилагательное + существительное
            elif token.pos_ == 'NOUN' and token.n_lefts >= 2:
                adjs = [child for child in token.lefts if child.pos_ == 'ADJ' and child.is_alpha]
                if len(adjs) == 2:
                    collocations.append(f"{adjs[0].text.capitalize()} {adjs[1].text} {token.text}")

            # Глагол с прямым дополнением
            elif token.pos_ == 'VERB' and token.n_rights > 0:
                for right in token.rights:
                    if right.dep_ in ['dobj', 'obj'] and '-' not in right.text and right.is_alpha:
                        collocations.append(f"{token.text.capitalize()} {right.text}")

    return Counter(collocations).most_common()