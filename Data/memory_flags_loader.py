import os
import json
from . import log_handler as log
flags = {}

json_path = os.path.join(os.path.dirname(__file__),"Long_term_memory","flag_dictionary.json")
def memory_load():
    global flags
    try:
        with open(json_path, 'r', encoding='utf-8') as flag_dict:
            flags = json.load(flag_dict)
        return ("Flag dictionary loaded", 0)
    except FileNotFoundError:
        log.data_collection("MEMORY", "LOAD_FILE", "Flag dictionary file not found.")
        return ("Bad memory file path", 1)
    except json.JSONDecodeError as e:
        log.data_collection("MEMORY", "LOAD_FILE", f"JSON parse error: {e}")
        return ("Malformed flag dictionary file", 1)

def flag_return(flag_name):
    global flags
    return flags.get(flag_name)

def flag_update(flag_name, value):
    global flags
    try:
        if isinstance(flags[flag_name], list):
            flags[flag_name].append(value)
            with open(json_path, 'w', encoding='utf-8') as flag_dict:
                json.dump(flags, flag_dict, indent=4)
            log.data_collection("MEMORY", "UPDATE_FLAG", f"Flag '{flag_name}' updated to '{value}'.")
        else:
            flags[flag_name] = value
            with open(json_path, 'w', encoding='utf-8') as flag_dict:
                json.dump(flags, flag_dict, indent=4)
            log.data_collection("MEMORY", "UPDATE_FLAG", f"Flag '{flag_name}' updated to '{value}'.")
    except Exception as e:
        log.data_collection("MEMORY", "UPDATE_FLAG", f"Error updating flag '{flag_name}': {e}")
