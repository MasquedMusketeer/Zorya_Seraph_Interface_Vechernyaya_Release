from . import (
    audio_play_module as apm,
    text_processing_module as tpm,
    memory_flags_loader as mfl,
    mood_engine_module as moem,
    log_handler as log
)
import threading as parallel
import random
import json
import os

response_library_file = os.path.join(os.path.dirname(__file__), "Long_term_memory","response_library.json")
response_library = {}

#__________________________________________________________________________________________________
#________________________________________ASSET HANDLER_____________________________________________
def load_response_library():
    global response_library
    try:
        with open(response_library_file, 'r', encoding='utf-8') as response_file:
            response_library = json.load(response_file)
        return ("Response library loaded", 0)
    except FileNotFoundError:
        return ("Bad response library file path", 1)
    except json.JSONDecodeError as e:
        return ("Malformed response library file", 1)

#__________________________________________________________________________________________________
#________________________________________MOOD SCORE HANDLER________________________________________
MOOD_RESPONSE_EXCEPTION = (
    "HAPPY", "MILD", "SAD", "REACTION", "BANTER",
    "JOKE", "FEATURES", "PCOFF", "SASS",
    "ALERT", "DEBUG", "VOCAB", "SILENT",
    "SUGGESTION", "FIRST_RUN", "START_UP", "TALK", "TRASH"
)

def get_line_index_by_score(category: str, valid_indices: list = None):
    try:
        category_responses = response_library.get(category, {})
        if not category_responses:
            return None
        
        # Filter by valid indices if provided
        if valid_indices:
            category_responses = {k: v for k, v in category_responses.items() if k in valid_indices}
        
        # Exception categories: random selection
        if category in MOOD_RESPONSE_EXCEPTION:
            return random.choice(list(category_responses.keys()))
        
        # Mood-based selection
        mood_compressed_score = moem.get_mood_compressed_score()
        line_mood_selected_score = moem.get_stochastic_score_based_on_mood_compression(mood_compressed_score)
        
        # Find all responses matching the mood score
        keys_matching_score = [
            key for key, response in category_responses.items() 
            if response.get("mood_score", 0) == line_mood_selected_score
        ]
        
        if not keys_matching_score:
            log.data_collection("RESPONSE HANDLER", "ERROR", 
                              f"No matching line index for score '{line_mood_selected_score}' in category '{category}'.")
            return None
        
        return random.choice(keys_matching_score)
        
    except Exception as e:
        log.data_collection("RESPONSE HANDLER", "ERROR", 
                          f"Error getting line index by score for category '{category}': {e}")
        return None

#__________________________________________________________________________________________________
#________________________________________LINE SELECTION____________________________________________
def _select_audio_text_line(category):
    try:
        last_used_line_cat = mfl.flag_return("last_phrase_type")
        last_used_line_id = mfl.flag_return("last_phrase_index")
        
        # Get all valid indices from response library
        valid_id_lines = list(response_library.get(category, {}).keys())
        
        # Remove last used line if same category
        if last_used_line_cat == category and last_used_line_id in valid_id_lines:
            valid_id_lines.remove(last_used_line_id)
        
        # Get line index based on mood
        line_index = get_line_index_by_score(category, valid_id_lines)
        
        if line_index is None:
            line_index = random.choice(valid_id_lines) if valid_id_lines else "0"
        
        mfl.flag_update("last_phrase_type", category)
        mfl.flag_update("last_phrase_index", line_index)
        return category, line_index
        
    except Exception as e:
        log.data_collection("RESPONSE HANDLER", "ERROR", f"Error selecting audio-text line: {e}")
        return category, "0"

#__________________________________________________________________________________________________
#________________________________________AUDIO TEXT SYNC___________________________________________
VOICE_ONLY_EXCEPTIONS = ["BANTER", "SASS","TRASH"]
def audio_text_synchronizer(category: str):
    try:
        category, line_index = _select_audio_text_line(category)
        
        # Get response data
        response = response_library.get(category, {}).get(line_index, {})
        text = response.get("text", "")
        audio_file = response.get("audio_file", "")
        
        # Use tpm to format text (handles multiline with /)
        dialogue_lines = tpm.clean_text(text)
        
        # Print text
        if category not in VOICE_ONLY_EXCEPTIONS:
            if isinstance(dialogue_lines, list) and dialogue_lines[0] == "MULTILINE":
                dialogue_lines.pop(0)
                for line in dialogue_lines:
                    print(line)
            else:
                print(dialogue_lines.strip("\n"))
        
        # Play audio using apm (pass just the filename)
        if audio_file:
            parallel.Thread(target=apm.play_line, args=(audio_file,), daemon=True).start()
            
    except Exception as e:
        log.data_collection("RESPONSE HANDLER", "ERROR", f"Error in audio-text synchronization: {e}")
        
def specific_line_audio_text_synchronizer(category: str, line_index: int):
    try:
        # Get response data
        response = response_library.get(category, {}).get(line_index, {})
        text = response.get("text", "")
        audio_file = response.get("audio_file", "")
        # Use tpm to format text (handles multiline with /)
        dialogue_lines = tpm.clean_text(text)
        # Print text
        if category not in VOICE_ONLY_EXCEPTIONS:
            if isinstance(dialogue_lines, list) and dialogue_lines[0] == "MULTILINE":
                dialogue_lines.pop(0)
                for line in dialogue_lines:
                    print(line)
            else:
                print(dialogue_lines.strip("\n"))
        # Play audio using apm (pass just the filename)
        if audio_file:
            parallel.Thread(target=apm.play_line, args=(audio_file,), daemon=True).start()
    except Exception as e:
        log.data_collection("RESPONSE HANDLER", "ERROR", f"Error in audio-text synchronization: {e}")

#__________________________________________________________________________________________________
#__________________________________SMALL RESPONSE HANDLER__________________________________________
def self_tell_joke(_):
    audio_text_synchronizer("JOKE")
    joke_count = mfl.flag_return("joke_count")
    mfl.flag_update("joke_count", (joke_count + 1))
    moem.self_alter_mood_tell_joke()
    
def respond_self_features(_):
    audio_text_synchronizer("FEATURES")
