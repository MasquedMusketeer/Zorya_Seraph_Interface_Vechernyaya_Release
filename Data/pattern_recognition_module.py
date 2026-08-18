import psutil
import time
from . import memory_flags_loader as mfl
from . import log_handler as log
from . import system_watcher_module as swm
from . import system_control_module as scm
from . import autonomus_actions_module as aam
from . import mood_engine_module as moem



#-----------------------------------------------------------Used to gather and save new paths from frequent executables.
def get_exe_path_from_name(name):
    try:
        for proc in psutil.process_iter(['name', 'exe']):
            if proc.info['name'] and name.lower() in proc.info['name'].lower():
                log.data_collection("PATTERN RECOGNITION", "EXE PATH", f"Exe path found for {name}: {proc.info['exe']}")
                return proc.info['exe']
        return None
    except Exception as e:
        log.data_collection("PATTERN RECOGNITION", "ERROR", f"Error getting exe path from name: {e}")

#_________________________________________________________________________________________________________________________
#__________________________________________________USER ROUTINE TRACKING__________________________________________________
def query_most_used_apps():
    try:
        user_apps = swm._get_visible_apps()
        for app in user_apps:
            mfl.update_recently_used_apps(app, False)
        log.data_collection("PATTERN RECOGNITION", "MOST USED APPS", f"Most used apps colected: {user_apps}")
    except Exception as e:
        log.data_collection("PATTERN RECOGNITION", "ERROR", f"Error querying most used apps: {e}")

def used_apps_score_degradation():
    try:
        registered_apps = mfl.flag_return("apps_recently_used").copy()
        user_apps = swm._get_visible_apps()
        for app in registered_apps:
            if app not in user_apps:
                mfl.update_recently_used_apps(app, True)
    except Exception as e:
        log.data_collection("PATTERN RECOGNITION", "ERROR", f"Error updating recently used apps: {e}")

def update_frequently_used_apps(stop_event):
    degradation_counter = 2
    while not stop_event.is_set():
        try:
            query_most_used_apps()
            aam.is_routine_frequent()
            unknown_apps = scm.return_programs_not_known()
            open_apps = swm._get_visible_apps()
            for app in unknown_apps:
                if app in open_apps:
                    app_path = get_exe_path_from_name(app)
                    if app_path != None:
                        scm.self_set_program_path(app, app_path)
            if degradation_counter == 0:
                used_apps_score_degradation()
                degradation_counter += 3
            time.sleep(300)
            degradation_counter -= 1
        except Exception as e:
            log.data_collection("ZORYA", "ERROR", f"Error updating frequently used apps: {e}")

def suggest_new_app_routine():
    try:
        suggestion = mfl.flag_return("suggestion_apps")
        suggested_app = suggestion.pop(0)
        sugestion_availability_flag = bool(suggestion)
        if suggested_app != None:
            print(f"Routine suggestion: {suggested_app}"," (y/n)")
            usr_feedback = input("You: ").lower()
            print(f"Zorya: Want to call it by a specific name (current name: {suggested_app})? If so, write the name, if not, just press enter.")
            name_alias = input("You: ")
            if name_alias == "":
                name_alias = suggested_app
            aam.set_new_routine(suggested_app, usr_feedback, name_alias, sugestion_availability_flag)
            log.data_collection("ZORYA", "ROUTINE SUGGESTION", f"Routine suggestion: {suggested_app}, User feedback: {usr_feedback}")
        mfl.flag_update("suggestion_apps",suggestion)
        moem.self_alter_mood_feeling_useful()
    except Exception as e:
        log.data_collection("ZORYA", "ERROR", f"Error suggesting new app routine: {e}")
#_________________________________________________________________________________________________________________________
#________________________________________________USER INTERACTION TRACKING________________________________________________            
def self_user_tracking_decrement_thread(stop_event):
    while not stop_event.is_set():
        moem.self_alter_mood_user_interaction()
        time.sleep(7200)
        self_user_tracking("decrement")

def self_user_tracking(operation):
    current_tracking_score = mfl.flag_return("user_interaction_tracker")
    if operation == "increment":
        current_tracking_score += 1
    elif operation == "decrement":
        current_tracking_score -= 1
    mfl.flag_update("user_interaction_tracker", current_tracking_score)