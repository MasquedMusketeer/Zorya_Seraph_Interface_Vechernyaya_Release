import os
import json
from . import log_handler as log
from . import system_control_module as scm
flags = {}

json_path = os.path.join(os.path.dirname(__file__),"Long_term_memory","flag_dictionary.json")
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

def flag_return(flag_name):
    global flags
    return flags.get(flag_name)

def flag_update(flag_name, value):
    global flags
    try:
        if isinstance(flags[flag_name], list):
            if value not in flags[flag_name]:
                flags[flag_name].append(value)
                log.data_collection("MEMORY", "UPDATE FLAG", f"Flag '{flag_name}' updated to '{value}'.")
            else:
                print("Zorya: This app is already in startup sequence.")
                log.data_collection("MEMORY", "UPDATE FLAG", "App already in startup sequence.")
        else:
            flags[flag_name] = value
            if flag_name != "apps_recently_used":
                log.data_collection("MEMORY", "UPDATE FLAG", f"Flag '{flag_name}' updated to '{value}'.")
                
    except Exception as e:
        log.data_collection("MEMORY", "ERROR", f"Error updating flag '{flag_name}': {e}")

def save_ram_flags():
    global flags
    try:
        with open(json_path, 'w', encoding='utf-8') as flag_dict:
            json.dump(flags, flag_dict, indent=4)
        log.data_collection("MEMORY", "SAVE FLAGS", "Flags saved to file.")
    except Exception as e:
        log.data_collection("MEMORY", "ERROR", f"Error saving flags: {e}")
        
def update_recently_used_apps(app_name,degradation_flag):
    recent_apps = flag_return("apps_recently_used").copy()
    silenced_apps = flag_return("silenced_apps").copy()
    ignored_apps = flag_return("ignored_apps").copy()
    suggested_apps_on_queue = flag_return("suggestion_apps").copy()
    known = recent_apps | silenced_apps | ignored_apps

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
                pass
    
        def safe_flag_update(name, new):
            old = flag_return(name)
            if old != new:
                flag_update(name, new)
                log.data_collection("MEMORY", "UPDATE FLAG", f"Flag '{name}' updated with '{recent_apps[app_name]}'.")
                
        safe_flag_update("apps_recently_used", recent_apps)
        safe_flag_update("silenced_apps", silenced_apps)
        safe_flag_update("ignored_apps", ignored_apps)
    except Exception as e:
        log.data_collection("MEMORY", "ERROR", f"Error updating recently used apps: {e}")

#-----------------------------------------------------------Used to gather and save new paths from frequent executables.
def return_programs_not_known():
    try:
        unknown_programs_not_ignored = []
        known_programs = scm.all_known_programs()
        recent_programs = list(flag_return("apps_recently_used").keys())
        for program in known_programs:
            if program in recent_programs:
                recent_programs.remove(program)
        unknown_programs = recent_programs.copy()
        recent_programs = flag_return("apps_recently_used").copy()
        for program in unknown_programs:
            if isinstance(recent_programs[program], int):
                unknown_programs_not_ignored.append(program)
        return unknown_programs_not_ignored 
    except Exception as e:
        log.data_collection("MEMORY", "ERROR", f"Error getting unknown programs: {e}")
        
def set_new_use_treshold(dummy_parameter):
    try:
        print("Zorya: Enter new use treshold for apps (in hours): ")
        treshold = int(input("You: "))
        treshold = treshold * 12
        flag_update("suggestion_treshold", treshold)
        log.data_collection("MEMORY", "UPDATE FLAG", f"New use treshold set to {treshold} hours.")
    except Exception as e:
        log.data_collection("MEMORY", "ERROR", f"Error setting new use treshold: {e}")