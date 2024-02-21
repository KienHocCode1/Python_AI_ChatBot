""" Trung Kien Bui 000356049, Mohawk College, Feb 12 2024 """
import string
import regex as re
import spacy
from spacy.matcher import Matcher


def load_FAQ_data():
    """This method reads and returns a list of questions and answers. The
    lists are parallel, meaning that intent n pairs with response n."""

    # read questions file turn it into list
    text_file_question = open('questions.txt','r')
    data = text_file_question.read()
    questions = data.split("\n")
    text_file_question.close()

    # read answers file turn it into list
    text_file_answer = open('answers.txt','r')
    data2 = text_file_answer.read()
    answers = data2.split("\n")
    text_file_answer.close()

    return questions, answers

def load_regex_patterns():
    """This method reads and returns a list of regex. The list is in fuzzy regular expression format."""

    text_file_regex = open('regex.txt', 'r')
    data3 = text_file_regex.read()
    regex_patterns = data3.split("\n")
    text_file_regex.close()

    return regex_patterns

def tailor_text(text):
    """This function removes whitespace, punctuation, and return the lowercase text from a given text."""

    # join splitted text(in list form atm), by using seperator '' (no spaces)
    text_no_whitespace = ''.join(text.split())

    # https://www.geeksforgeeks.org/python-remove-punctuation-from-string/
    # remove punctuations
    text_no_punctuation = text_no_whitespace.translate(str.maketrans("", "", string.punctuation))

    return text_no_punctuation.lower()

def identify_entities(text):
    """This function uses spaCy to identify entities such as organizations (ORG), geopolitical entities (GPE), and nouns in the given text. Then results will be used to reponds errors message accordingly in def generate()"""

    # Load spaCy model with medium-sized English word vectors
    nlp = spacy.load("en_core_web_md")
    # Initialize spaCy Matcher
    matcher = Matcher(nlp.vocab)

    # Define a pattern for identifying location phrases
    pattern = [
        {"LEMMA": {"IN": ["be", "were", "go", "walk", "move", "travel", "head", "tell"]}, "OP": "?"},
        {"LOWER": {"IN": ["to", "into", "toward", "for"]}, "OP": "?"},
        {"POS": "DET", "OP": "?"},
        {"POS": {"IN": ["ADJ", "PUNCT", "ADV"]}, "OP": "*"},
        {"POS": {"IN": ["PROPN", "NOUN"]}, "ENT_TYPE": {"IN": ["ORG", "GPE", "NOUN"]}, "OP": "?"}
    ]

    # Add the pattern to the Matcher with the label "location phrase"
    matcher.add("location phrase", [pattern])
    # Process the text using spaCy
    doc = nlp(text)
    # Use the Matcher to find matches in the processed text
    matches = matcher(doc)

    # Initialize a dictionary to store identified entities
    types = {"ORG": None, "GPE": None, "NOUN": None}

    #https://stackoverflow.com/questions/70450784/spacy-entity-ruler-pattern-isnt-working-for-ent-type
    # Iterate through matches and identify entities
    for match_id, start, end in matches:
        matched_span = doc[start:end]
        if matched_span.root.ent_type_ == "ORG":
            types["ORG"] = matched_span.text
            break
        elif matched_span.root.ent_type_ == "GPE":
            types["GPE"] = matched_span.text
            break

    # Iterate through noun chunks and identify nouns
    for chunk in doc.noun_chunks:
        types["NOUN"] = chunk.text
        break # Take first noun then stop

    #print("This is identify_entities:", types)
    return types

def understand(utterance):
    """This method processes an utterance to determine which intent it
    matches. The index of the intent is returned, or -1 if no intent
    is found."""

    global intents # declare that we will use a global variable
    utterance_processed = tailor_text(utterance) #Phase 0

    # Load regex patterns for additional intent matching
    regex_patterns = load_regex_patterns()
    #print(regex_patterns)

    try:
        intents_processed = [tailor_text(intent) for intent in intents] #Phase 0

        # Iterate through processed intents and regex patterns
        for i, (intent, regex_pattern) in enumerate(zip(intents_processed, regex_patterns)):
            # Check if the utterance matches the processed intent or regex pattern
            if re.match(intent, utterance_processed) or re.match(regex_pattern, utterance_processed):
                return i # Return the index of the matched intent

        return -1 # Return -1 if no intent matches

    except ValueError:
        return -1

def generate(intent, utterance): #added 2nd argument: utterance
    """This function returns an appropriate response given a user's intent."""

    global responses # declare that we will use a global variable

    # Identify entities in the utterance using the identify_entities function
    entities = identify_entities(utterance)
    #print("This is generate", entities)

    # Check if no intent is found and respond according to types
    if intent == -1:
        if entities["GPE"]:
            return f"Sorry, I don't know where {entities['GPE']} is."

        if entities["ORG"]:
            return f"Sorry, I don't have information about {entities['ORG']}."

        if entities["NOUN"]:
            if entities["NOUN"].lower() == "i":
                return f"Sorry, my creator has not taught me how to answer to this. Can you rephrase it?"
            else:
                return f"Sorry, I don't have details about {entities['NOUN']}."

        # Default response when no intent or entities are identified
        return "I'm sorry, but I couldn't understand your question. Can you please provide more details or rephrase?"

    return responses[intent]


## Load the questions and responses
intents, responses = load_FAQ_data()

## Main Function

def main():
    """Implements a chat session in the shell."""
    print("Hello! I'm created to answer questions'. When you're done talking, just say 'goodbye'.")
    print()
    utterance = ""
    while True:
        utterance = input(">>> ")
        if utterance == "goodbye":
            break;
        intent = understand(utterance)
        response = generate(intent, utterance) #added 2nd argument: utterance
        print("\n"+response)
        print()

    print("\nNice talking to you!")

## Run the chat code
# the if statement checks whether or not this module is being run
# as a standalone module. If it is beign imported, the if condition
# will be false and it will not run the chat method.
if __name__ == "__main__":
    main()