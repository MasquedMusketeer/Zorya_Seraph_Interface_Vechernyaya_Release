import os
import re
import json
from . import log_handler as log

vocabulary_path = os.path.join(os.path.dirname(__file__), "Long_term_memory","known_vocabulary.json")
intent_map_path = os.path.join(os.path.dirname(__file__), "Long_term_memory","intent_map.json")
short_memory_path = os.path.join(os.path.dirname(__file__), "Long_term_memory", "routine_buffer.json")
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
            if "OBJECT.SELF" in token:
                token = "OBJECT.SELF"
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

def _check_routine_existance(intent_name):
    global intent_map
    if intent_name in intent_map:
        return True
    else:
        return False

def get_best_partial_match(input_tokens: list) -> tuple:
    global intent_map
    input_tokens_set = set(input_tokens)
    best_match = (None, 0) # (intent_id, score)
    
    for intent_id, intent_data in intent_map.items():
        required_tokens = intent_data.get("tokens", [])
        match_score = 0

        for required_prefix in required_tokens:
            token_found = any(
                input_token.startswith(required_prefix) 
                for input_token in input_tokens_set
            )
            if token_found:
                match_score += 1
        if match_score > best_match[1]:
            best_match = (intent_id, match_score)
            
    return best_match

def save_new_routine():
    global intent_map
    global short_memory_path
    global intent_map_path
    try:
        if os.path.getsize(short_memory_path) > 2:
            with open(short_memory_path, 'r', encoding='utf-8') as short_memory_file:
                short_memory = json.load(short_memory_file)
                intent_map.update(short_memory)
                with open(intent_map_path, 'w', encoding='utf-8') as intent_map_file:
                    json.dump(intent_map, intent_map_file, indent=4)
                short_memory.clear()
                with open(short_memory_path, 'w', encoding='utf-8') as short_memory_file:
                    json.dump(short_memory, short_memory_file, indent=4)
                log.data_collection("ROUTINE SAVING", "SAVE", "New intent added to mapped intents.")
        else:
            log.data_collection("ROUTINE SAVING", "SAVE", "No new intent found.")
    except Exception as e:
        log.data_collection("ROUTINE SAVING", "SAVE", f"Error saving new intent: {e}")
        
def save_new_vocabulary(category_subcategory_word):
    global vocabulary
    global vocabulary_path
    category, subcategory, word = category_subcategory_word.split(".")
    if word == "":
        log.data_collection("VOCABULARY", "SAVE", "Empty word not saved.")
        return
    try:
        if word in vocabulary[category][subcategory]:
            log.data_collection("VOCABULARY", "SAVE", f"Word {word} already exists in category {category}.{subcategory}")
            return
        else:
            vocabulary.setdefault(category, {}).setdefault(subcategory, []).append(word)
            with open(vocabulary_path, 'w', encoding='utf-8') as vocab_file:
                json.dump(vocabulary, vocab_file, indent=4)
            log.data_collection("VOCABULARY", "SAVE", f"New word learned {word} in category {category}.{subcategory}")
    except Exception as e:
        log.data_collection("VOCABULARY", "SAVE", f"Error saving vocabulary: {e}")
        
def flush_memory():
    global intent_map
    intent_map.clear()
    log.data_collection("MEMORY", "FLUSH", "Intent map flushed from runtime memory.")