import os
import re
import json
from . import log_handler as log

vocabulary_path = os.path.join(os.path.dirname(__file__), "Long_term_memory","known_vocabulary.json")
intent_map_path = os.path.join(os.path.dirname(__file__), "Long_term_memory","intent_map.json")
vocabulary = {}
word_to_token = {}
intent_map = {}

def vocabulary_load():
    global vocabulary
    global word_to_token
    try:
        with open(vocabulary_path, 'r', encoding='utf-8') as vocab_file:
            vocabulary = json.load(vocab_file)
            for category, subdict in vocabulary.items():
                if isinstance(subdict, dict):
                    for subcat, wordlist in subdict.items():
                        for word in wordlist:
                            word_to_token[word] = f"{category}.{subcat}.{word}"
        return ("Vocabulary loaded", 0)
    except FileNotFoundError:
        log.data_collection("VOCABULARY", "LOAD_FILE", "Vocabulary file not found.")
        return ("Bad vocabulary file path", 1)
    except json.JSONDecodeError as e:
        log.data_collection("VOCABULARY", "LOAD_FILE", f"JSON parse error: {e}")
        return ("Malformed vocabulary file", 1)

def intent_map_load():
    global intent_map
    try:
        with open(intent_map_path, 'r', encoding='utf-8') as intent_file:
            intent_map = json.load(intent_file)
        return ("Intent map loaded", 0)
    except FileNotFoundError:
        log.data_collection("INTENT_MAP", "LOAD_FILE", "Intent map file not found.")
        return ("Bad intent map file path", 1)
    except json.JSONDecodeError as e:
        log.data_collection("INTENT_MAP", "LOAD_FILE", f"JSON parse error: {e}")
        return ("Malformed intent map file", 1)
    
def phrase_tokenizer(usr_phrase):
    log.data_collection("VOCABULARY", "TOKENIZE", f"Tokenizing phrase: {usr_phrase.upper()}")
    tokens = []
    words = re.sub(r"[^\w\s]", "", usr_phrase.lower()).split()
    for word in words:
        if word in word_to_token: # Direct, fast lookup
            token = word_to_token[word]
            if "ACTION.OPEN" in token:
                token = "ACTION.OPEN"
            if "ACTION.QUERY" in token:
                token = "ACTION.QUERY"
            tokens.append(token)
            log.data_collection("VOCABULARY", "TOKENIZE", f"Matched word '{word}' to token '{token}'")
    
    return tokens

def interpret_tokens(phrase):
    token_buffer = phrase_tokenizer(phrase)
    input_tokens_set = set(token_buffer)
    
    for intent_name, intent_data in intent_map.items():
        required_tokens = intent_data.get("tokens", [])
        is_match = True
        for required_prefix in required_tokens:
            token_found = any(
                input_token.startswith(required_prefix) 
                for input_token in input_tokens_set
            )
            if not token_found:
                is_match = False
                break
        if is_match:
            log.data_collection("INTERPRETATION", "DETECT INTENT", f"Contract: {(intent_name,intent_data.get("action_module"),intent_data.get("action_function"),intent_data.get("parameters", {}))}")
            #return contract
            return (
                intent_name,
                intent_data.get("action_module"),
                intent_data.get("action_function"),
                intent_data.get("parameters", {})
            )
        
    log.data_collection("INTERPRETATION", "DETECT INTENT", "No intent matched after checking all possibilities.")
    return (None)
            