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

#_________________________________________________________________________________________________________________________
#____________________________________________________ASSETS HANDLER_______________________________________________________
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
#_________________________________________________________________________________________________________________________
#______________________________________________________API HANDLER________________________________________________________
def map_intent_to_response(intent_id: str) -> str:
    if intent_id is None:
        return "ERROR"
    intent_id = intent_id.upper()
    response_exceptions = {
            "INTENT_QUERY_SELF",
            "INTENT_QUERY_STATUS",
            "INTENT_QUERY_TIME",
            "INTENT_REPORT_SELF_INTENT",
            "INTENT_REPORT_SELF_RECENT_LOGS",
            "INTENT_PING_SITE",
            "INTENT_QUERY_LAST_BACKUP"
            }
    if intent_id in response_exceptions:
        return "EXCEPTION"
    else:
        if intent_id.startswith(("INTENT_RUN_", "INTENT_OPEN_", "INTENT_SET_","INTENT_BUILD_","INTENT_SSH_", "INTENT_CORRECT_")) or intent_id.endswith(("_CMD","_BATCH","_PROGRAM","_BACKUP")):
            return "EXECUTION"
        if intent_id.startswith("INTENT_STOP_"):
            return "BYE"
        if intent_id.startswith(("INTENT_TELL_", "INTENT_JOKE_")):
            return "JOKE"
        if intent_id == "INTENT_QUERY_FEATURES":
            return "FEATURES"
        if intent_id.endswith(("_OVERRIDE1", "_OVERRIDE2")):
            return "DEBUG"
        if intent_id.startswith("INTENT_MUTE_"):
            return "SILENT"
        if intent_id.startswith("INTENT_TALK_"):
            return "TALK"
        if intent_id.endswith("_NEW_VOCAB"):
            return "VOCAB"
        
        return "EXECUTION"
#_________________________________________________________________________________________________________________________
#_______________________________________________INTERPRETATION HANDLER____________________________________________________
def phrase_tokenizer(usr_phrase):
    log.data_collection("INTERPRETATION ENGINE", "TOKENIZE", f"Tokenizing phrase: {usr_phrase.upper()}")
    tokens = []
    words = re.sub(r"[^\w\s]", "", usr_phrase.lower()).split()
    for word in words:
        if word in word_to_token: # Direct, fast lookup
            token = word_to_token[word]
            if "ACTION.OPEN" in token:
                token = "ACTION.OPEN"
            if "ACTION.CREATE" in token:
                token = "ACTION.CREATE"
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
#_________________________________________________________________________________________________________________________
#____________________________________________________INTENT HANDLER_______________________________________________________
def _check_routine_existance(intent_name):
    global intent_map
    global short_memory_path
    if intent_name in intent_map or intent_name in short_memory_path:
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
#_________________________________________________________________________________________________________________________
#_________________________________________________VOCABULARY HANDLER______________________________________________________
def get_all_vocab_classifications():
    global vocabulary
    all_current_vocab = []
    for category, subdict in vocabulary.items():
        if isinstance(subdict, dict):
            vocab_cat_buffer = [f"{category}.{subcat}" for subcat in subdict.keys()]
            line = f"{category}: " + ", ".join(vocab_cat_buffer)
            all_current_vocab.append(line)
    return all_current_vocab

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

def _save_vocabulary(category_subcategory_word):
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

def save_new_vocab(_):
    try:
        print("Zorya: What is the new word?")
        new_word = input("You: ").strip(" ").lower()
        if not new_word:
            print("Zorya: You dont expect me to believe your 'word' exists, right?")
            return
        print("Zorya: Fine. What category does this alleged word belong to?")
        print("Zorya: Here are the ones I *already* know, not that you checked before asking:")
        all_categories = get_all_vocab_classifications()
        for cat in all_categories:
            print(cat)
        category = input("You: ")
        category = category.strip().upper()
        if "." not in category:
            print("Zorya: That's not a category. That's... whatever that is. Try again when you're coherent.")
            return
        vocab_param = f"{category}.{new_word}"
        _save_vocabulary(vocab_param)
        print("Zorya: Well, congrats, at least you didn't break me this time.")
        moem.self_alter_mood_new_words()
    except Exception as e:
        log.data_collection("SYSTEM", "ERROR", f"Error saving new vocabulary: {e}")
        print("Zorya: I'm not sure what happened, but definetly wasn't supposed to. Try again with the brain on.")
#_________________________________________________________________________________________________________________________
#______________________________________________STALE INTENTS SANITIZER____________________________________________________
def sanitize_stale_program_intents(known_programs):
    try:
        stale_sanitized_intents = []
        for intent_key in list(intent_map.keys()):
            if intent_key.startswith("INTENT_OPEN_") and intent_map[intent_key]["action_function"] == "call_program":
                program_name = intent_map[intent_key]["parameters"]
                if program_name not in known_programs:
                    delete_intent(intent_key)
                    stale_sanitized_intents.append(intent_key)
        if stale_sanitized_intents:
            with open(intent_map_path, 'w', encoding='utf-8') as intent_map_file:
                json.dump(intent_map, intent_map_file, indent=4)
            log.data_collection("INTERPRETATION ENGINE", "SANITIZE INTENTS", f"Sanitized stale intents: {stale_sanitized_intents}")
            return (f"Sanitized intents: {stale_sanitized_intents}",0)
        else:
            log.data_collection("INTERPRETATION ENGINE", "SANITIZE INTENTS", "No stale intents found.")
            return ("No stale intents found.", 0)
    except Exception as e:
        log.data_collection("INTERPRETATION ENGINE", "ERROR", f"Error sanitizing stale intents: {e}")
        return (f"Error sanitizing stale intents: {e}", 1)
