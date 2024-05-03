import spacy
from spacy.matcher import Matcher


def load_and_process_text(filename):
    with open(filename, 'r') as file:
        text = file.read()
    return text


def setup_spacy():
    # Load the spaCy model
    nlp = spacy.load("en_core_web_trf");
    print("[spaCy]: The model has been successfully loaded")
    matcher = Matcher(nlp.vocab)

    # Define patterns corresponding to sign-post structures
    patterns = [
        [{"LOWER": "this"}, {"LOWER": "paper"}, {"LOWER": "proposes"}],  # This paper proposes
        [{"LOWER": "numerical"}, {"LOWER": "results"}, {"LOWER": "show"}],  # Numerical results show
        [{"LOWER": "we"}, {"LOWER": "introduce"}],  # We introduce
        [{"LOWER": "using"}, {"LOWER": "this"}, {"LOWER": "approach"}, {"LOWER": "we"}, {"LOWER": "formulate"}], # Using this approach we formulate
        [{"LOWER": "we"}, {"LOWER": "show"}, {"LOWER": "how"}, {"LOWER": "methods"}, {"LOWER": "with"}], # We show how methods with
        [{"LOWER": "we"}, {"LOWER": "demonstrate"}, {"LOWER": "our"}, {"LOWER": "approach"}, {"LOWER": "on"}], # We demonstrate our approach on
        [{"LOWER": "this"}, {"LOWER": "allows"}, {"LOWER": "us"}, {"LOWER": "to"}],  # This allows us to
        [{"LOWER": "is"}, {"LOWER": "considered"}, {"LOWER": "within"}, {"LOWER": "the"}, {"LOWER": "context"}, {"LOWER": "of"}],  # is considered within the context of
        [{"LOWER": "the"}, {"LOWER": "goal"}, {"LOWER": "is"}, {"LOWER": "to"}, {"LOWER": "produce"}], # The goal is to produce
        [{"LOWER": "this"}, {"LOWER": "is"}, {"LOWER": "achieved"}, {"LOWER": "by"}, {"LOWER": "means"}, {"LOWER": "of"}],  # This is achieved by means of
        [{"LOWER": "the"}, {"LOWER": "benefit"}, {"LOWER": "of"}, {"LOWER": "the"}, {"LOWER": "proposed"}, {"LOWER": "framework"}, {"LOWER": "is"}, {"LOWER": "illustrated"}], # The benefit of the proposed framework is illustrated
        [{"LOWER": "the"}, {"LOWER": "full"}, {"LOWER": "power"}, {"LOWER": "of"}, {"LOWER": "the"}, {"LOWER": "approach"}, {"LOWER": "is"}, {"LOWER": "further"}, {"LOWER": "exemplified"}], # The full power of the approach is further exemplified
        [{"LOWER": "this"}, {"LOWER": "manuscript"}, {"LOWER": "reports"}, {"LOWER": "the"}, {"LOWER": "findings"}], # This manuscript reports the findings
        [{"LOWER": "data"}, {"LOWER": "analysis"}, {"LOWER": "suggests"}],  # Data analysis suggests
        [{"LOWER": "these"}, {"LOWER": "findings"}, {"LOWER": "have"}, {"LOWER": "implications"}, {"LOWER": "for"}], # These findings have implications for
        [{"LOWER": "the"}, {"LOWER": "authors"}, {"LOWER": "are"}, {"LOWER": "grateful"}],  # The authors are grateful
        [{"LOWER": "are"}, {"LOWER": "collaborators"}, {"LOWER": "on"}],  # are collaborators on
        [{"LOWER": "this"}, {"LOWER": "research"}, {"LOWER": "is"}, {"LOWER": "supported"}, {"LOWER": "by"}], # This research is supported by
        [{"LOWER": "we"}, {"LOWER": "appreciate"}, {"LOWER": "the"}, {"LOWER": "insightful"}, {"LOWER": "comments"}], # We appreciate the insightful comments
        [{"LOWER": "this"}, {"LOWER": "material"}, {"LOWER": "is"}, {"LOWER": "based"}, {"LOWER": "upon"}, {"LOWER": "work"}, {"LOWER": "supported"}, {"LOWER": "by"}]  # This material is based upon work supported by
    ]

    # Add patterns to the matcher
    for pattern in patterns:
        matcher.add("SIGN_POST", [pattern])

    return nlp, matcher


def find_sign_posts(text, nlp, matcher):
    text = text.lower()
    text.replace('.', '')
    doc = nlp(text)
    matches = matcher(doc)
    matched_sentences = set()  # Use a set to avoid duplicates

    for match_id, start, end in matches:
        # Extract the sentence containing the matched span
        sentence = doc[start:end].sent
        matched_sentences.add(sentence.text)

    return matched_sentences


# Main execution
if __name__ == "__main__":
    text = load_and_process_text('debug/pdf.txt')  # Replace with your article file path
    nlp, matcher = setup_spacy()
    sign_posts = find_sign_posts(text, nlp, matcher)
    for post in sign_posts:
        print(post)