import os
import json
from . import log_handler as log
import threading
import copy

_flag_lock = threading.Lock()
flags = {}

json_path = os.path.join(os.path.dirname(__file__),"Long_term_memory","flag_dictionary.json")
#__________________________________________________________________________________________________
#________________________________________ASSET HANDLER_____________________________________________
def memory_load():
    global flags
    try:
        with open(json_path, 'r', encoding='utf-8') as flag_dict:
            flags = json.load(flag_dict)
        return ("Flag dictionary loaded", 0)
    except FileNotFoundError:
        log.data_collection("MEMORY", "ERROR", "Flag dictionary file not found.")
        return ("Bad memory file path", 1)
    except json.JSONDecodeError as e:
        log.data_collection("MEMORY", "ERROR", f"JSON parse error: {e}")
        return ("Malformed flag dictionary file", 1)
#__________________________________________________________________________________________________
#____________________________________INPUT/OUTPUT HANDLER__________________________________________
def state_return():
    with _flag_lock:
        global flags
        return copy.deepcopy(flags)

def flag_return(flag_name):
    with _flag_lock:
        value = flags.get(flag_name)
        return copy.deepcopy(value)

def flag_update(flag_name, value):
    with _flag_lock:
        try:
            flags[flag_name] = value
            if flag_name != "apps_recently_used":
                log.data_collection("MEMORY", "UPDATE FLAG",f"Flag '{flag_name}' updated to '{value}'.")
        except Exception as e:
            log.data_collection("MEMORY", "ERROR",f"Error updating flag '{flag_name}': {e}")
#__________________________________________________________________________________________________
#_________________________________PERIODIC MEMORY MODIFICATIONS____________________________________
def save_ram_flags():
    global flags
    try:
        with open(json_path, 'w', encoding='utf-8') as flag_dict:
            json.dump(flags, flag_dict, indent=4)
        log.data_collection("MEMORY", "SAVE FLAGS", "Flags saved to file.")
    except Exception as e:
        log.data_collection("MEMORY", "ERROR", f"Error periodic saving of flags: {e}")

def periodic_save_ram_flags_to_disk(stop_event):
    while not stop_event.is_set():
        save_ram_flags()
        stop_event.wait(300)
#__________________________________________________________________________________________________
#_______________________________________APP SCORE TRACKER__________________________________________     
def update_recently_used_apps(app_name,degradation_flag):
    recent_apps = flag_return("apps_recently_used").copy()
    silenced_apps = flag_return("silenced_apps").copy()
    ignored_apps = flag_return("ignored_apps").copy()
    suggested_apps_on_queue = flag_return("suggestion_apps").copy()
    known = recent_apps | silenced_apps | ignored_apps
    deleted_app = []

    try:
        if degradation_flag == False:
            if app_name not in known:
                recent_apps[app_name] = 1
                log.data_collection("MEMORY", "UPDATE FLAG", f"New app added to recently used: {app_name}")
            elif app_name in recent_apps and app_name not in suggested_apps_on_queue:
                recent_apps[app_name] += 1
        elif degradation_flag == True:
            if app_name in recent_apps:
                recent_apps[app_name] -= 1
                if recent_apps[app_name] <= 0:
                    del recent_apps[app_name]
                    deleted_app.append(app_name)
    
        def safe_flag_update(name, new):
            old = flag_return(name)
            if old != new:
                flag_update(name, new)
                if deleted_app:
                    log.data_collection("MEMORY", "UPDATE FLAG", f"App(s) removed from {name}: {deleted_app}")
                    deleted_app.clear()
                elif name == "apps_recently_used":
                    log.data_collection("MEMORY", "UPDATE FLAG", f"Flag '{app_name}' updated with '{recent_apps[app_name]}'.")
                else:
                    log.data_collection("MEMORY", "UPDATE FLAG", f"Flag '{name}' updated.")
                
        safe_flag_update("apps_recently_used", recent_apps)
        safe_flag_update("silenced_apps", silenced_apps)
        safe_flag_update("ignored_apps", ignored_apps)
    except Exception as e:
        log.data_collection("MEMORY", "ERROR", f"Error updating recently used apps: {e}")

def set_new_use_treshold(_):
    try:
        print("Zorya: Enter new use treshold for apps (in hours): ")
        treshold = int(input("You: "))
        treshold = treshold * 12
        flag_update("suggestion_treshold", treshold)
        log.data_collection("MEMORY", "UPDATE FLAG", f"New use treshold set to {treshold} hours.")
    except Exception as e:
        log.data_collection("MEMORY", "ERROR", f"Error setting new use treshold: {e}")
#__________________________________________________________________________________________________
#______________________________________MEMORY SANITIZATION_________________________________________ 
def sanitize_memory_programs(known_programs):
    try:
        silenced_apps = flag_return("silenced_apps")
        ignored_apps = flag_return("ignored_apps")
        apps_expected_at_start = flag_return("apps_expected_at_start")
        sanitized_entries = []
        for app in list(silenced_apps.keys()):
            if app not in known_programs:
                if app not in sanitized_entries:
                    sanitized_entries.append(app)
                del silenced_apps[app]
        for app in list(apps_expected_at_start):
            if app not in known_programs:
                if app not in sanitized_entries:
                    sanitized_entries.append(app)
                apps_expected_at_start.remove(app)
        if sanitized_entries:
            flag_update("silenced_apps", silenced_apps)
            flag_update("ignored_apps", ignored_apps)
            flag_update("apps_expected_at_start", apps_expected_at_start)
            log.data_collection("MEMORY", "SANITIZE", "Memory sanitized from deleted programs.")
            return (f"Sanitized memory entries: {sanitized_entries}", 0)
        else:
            log.data_collection("MEMORY", "SANITIZE", "No memory entries to sanitize.")
            return ("No entries to sanitize.", 0)
    except Exception as e:
        log.data_collection("MEMORY", "ERROR", f"Error sanitizing memory: {e}")
        return (f"Error sanitizing memory: {e}", 1)
