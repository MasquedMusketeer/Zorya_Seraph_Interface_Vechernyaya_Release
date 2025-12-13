import os
import re
import json
from . import log_handler as log
from . import mood_engine_module as moem

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
        log.data_collection("INTERPRETATION ENGINE", "ERROR", "Vocabulary file not found.")
        return ("Bad vocabulary file path", 1)
    except json.JSONDecodeError as e:
        log.data_collection("INTERPRETATION ENGINE", "ERROR", f"JSON parse error: {e}")
        return ("Malformed vocabulary file", 1)

def intent_map_load():
    global intent_map
    try:
        with open(intent_map_path, 'r', encoding='utf-8') as intent_file:
            intent_map = json.load(intent_file)
        return ("Intent map loaded", 0)
    except FileNotFoundError:
        log.data_collection("INTERPRETATION ENGINE", "ERROR", "Intent map file not found.")
        return ("Bad intent map file path", 1)
    except json.JSONDecodeError as e:
        log.data_collection("INTERPRETATION ENGINE", "ERROR", f"JSON parse error: {e}")
        return ("Malformed intent map file", 1)

def phrase_tokenizer(usr_phrase):
    log.data_collection("INTERPRETATION ENGINE", "TOKENIZE", f"Tokenizing phrase: {usr_phrase.upper()}")
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
            log.data_collection("INTERPRETATION ENGINE", "TOKENIZE", f"Matched word '{word}' to token '{token}'")
    
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
            log.data_collection("INTERPRETATION ENGINE", "DETECT INTENT", f"Contract: {(intent_name,intent_data.get("action_module"),intent_data.get("action_function"),intent_data.get("parameters", {}))}")
            #return contract
            return (
                intent_name,
                intent_data.get("action_module"),
                intent_data.get("action_function"),
                intent_data.get("parameters", {})
            )
        
    log.data_collection("INTERPRETATION ENGINE", "DETECT INTENT", "No intent matched after checking all possibilities.")
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
                log.data_collection("INTERPRETATION ENGINE", "SAVE ROUTINE", "New intent added to mapped intents.")
        else:
            log.data_collection("INTERPRETATION ENGINE", "SAVE ROUTINE", "No new intent found.")
    except Exception as e:
        log.data_collection("INTERPRETATION ENGINE", "ERROR", f"Error saving new intent: {e}")
        
def save_new_vocabulary(category_subcategory_word):
    global vocabulary
    global vocabulary_path
    category, subcategory, word = category_subcategory_word.split(".")
    if word == "":
        log.data_collection("INTERPRETATION ENGINE", "SAVE VOCAB", "Empty word not saved.")
        return
    try:
        if word in vocabulary[category][subcategory]:
            log.data_collection("INTERPRETATION ENGINE", "SAVE VOCAB", f"Word {word} already exists in category {category}.{subcategory}")
            return
        else:
            vocabulary.setdefault(category, {}).setdefault(subcategory, []).append(word)
            with open(vocabulary_path, 'w', encoding='utf-8') as vocab_file:
                json.dump(vocabulary, vocab_file, indent=4)
            moem.self_alter_mood_new_words()
            log.data_collection("INTERPRETATION ENGINE", "SAVE VOCAB", f"New word learned {word} in category {category}.{subcategory}")
    except Exception as e:
        log.data_collection("INTERPRETATION ENGINE", "ERROR", f"Error saving vocabulary: {e}")
        
def flush_memory():
    global intent_map
    intent_map.clear()
    log.data_collection("INTERPRETATION ENGINE", "FLUSH", "Intent map flushed from runtime memory.")
    
def get_all_intents():
    global intent_map
    all_current_intents = []
    for intent_name, intent_data in intent_map.items():
        all_current_intents.append(intent_name)
    return all_current_intents

def get_single_intent(intent_name):
    global intent_map
    if intent_name in intent_map:
        return intent_map[intent_name]
    else:
        return None

def get_all_vocab_classifications():
    global vocabulary
    all_current_vocab = []
    for category, subdict in vocabulary.items():
        if isinstance(subdict, dict):
            vocab_cat_buffer = [f"{category}.{subcat}" for subcat in subdict.keys()]
            line = f"{category}: " + ", ".join(vocab_cat_buffer)
            all_current_vocab.append(line)
    return all_current_vocab

def delete_intent(intent_name):
    global intent_map
    try:
        if intent_name in intent_map:
            del intent_map[intent_name]
            log.data_collection("INTERPRETATION ENGINE", "DELETE INTENT", f"Intent {intent_name} deleted.")
        else:
            log.data_collection("INTERPRETATION ENGINE", "DELETE INTENT", f"Intent {intent_name} not found.")
    except Exception as e:
        log.data_collection("INTERPRETATION ENGINE", "ERROR", f"Error deleting intent: {e}")

def delete_vocabulary(category_subcategory_word):
    global vocabulary
    global vocabulary_path
    category, subcategory, word = category_subcategory_word.split(".")
    try:
        if word in vocabulary[category][subcategory]:
            vocabulary[category][subcategory].remove(word)
            with open(vocabulary_path, 'w', encoding='utf-8') as vocab_file:
                json.dump(vocabulary, vocab_file, indent=4)
            log.data_collection("INTERPRETATION ENGINE", "DELETE VOCAB", f"Word {word} deleted from category {category}.{subcategory}")
        else:
            log.data_collection("INTERPRETATION ENGINE", "DELETE VOCAB", f"Word {word} not found in category {category}.{subcategory}")
    except Exception as e:
        log.data_collection("INTERPRETATION ENGINE", "ERROR", f"Error deleting vocabulary: {e}")