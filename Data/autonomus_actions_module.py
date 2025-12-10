from . import log_handler as log
from . import memory_flags_loader as mfl
from . import system_control_module as scm
from . import interpretation_engine as interpreter
from . import routine_builder_module as rbm
from . import mood_engine_module as moem


def is_routine_frequent():
    try:
        all_current_intents = interpreter.get_all_intents()
        recent_apps = mfl.flag_return("apps_recently_used").copy()
        silenced_apps = mfl.flag_return("silenced_apps").copy()
        old_recent_apps = mfl.flag_return("apps_recently_used")
        old_silenced_apps = mfl.flag_return("silenced_apps")
        # --- PHASE 1: Move recent apps that match intents to silenced ---
        apps_to_silence = []
        for app in recent_apps:
            for intent in all_current_intents:
                if app.upper() in intent:
                    apps_to_silence.append(app)
                    break
        for app in apps_to_silence:
            recent_apps.pop(app, None)
            silenced_apps[app] = "silence"
        if old_recent_apps != recent_apps:
            mfl.flag_update("apps_recently_used", recent_apps)
        if old_silenced_apps != silenced_apps:
            mfl.flag_update("silenced_apps", silenced_apps)
        # --- PHASE 2: Check for frequent routines ---
        suggestion_threshold = mfl.flag_return("suggestion_treshold")
        suggested_apps_in_queue = mfl.flag_return("suggestion_apps")
        for app, score in recent_apps.items():
            if score >= suggestion_threshold and app not in suggested_apps_in_queue:
                log.data_collection("AUTONOMUS ACTIONS", "ROUTINE FREQUENT",f"Routine frequency threshold reached for: {app}")
                mfl.flag_update("have_suggestion", True)
                mfl.flag_update("suggestion_apps", app)
        return None
        
    except Exception as e:
        log.data_collection("AUTONOMUS ACTIONS", "ERROR", f"Error checking routine frequent: {e}")
        return None

def set_new_routine(suggestion, usr_feedback):
    try:
        flag_update = mfl.flag_return("apps_recently_used")
        silenced_apps = mfl.flag_return("silenced_apps")
        ignored_apps = mfl.flag_return("ignored_apps")
        pop_app = ""
        if usr_feedback == "y":
            scm.self_temp_to_disk(suggestion)
            rbm.self_build_routine(f"INTENT_OPEN_{suggestion.upper()}",f"open the app {suggestion}",["ACTION.OPEN",f"OBJECT.APP.{suggestion}"],"system_control_module","call_program",suggestion)
            for app in flag_update:
                if suggestion == app:
                    silenced_apps[app] = "silence"
                    mfl.flag_update("silenced_apps", silenced_apps)
                    pop_app = app
            flag_update.pop(pop_app)
            mfl.flag_update("apps_recently_used", flag_update)
            interpreter.save_new_vocabulary(f"OBJECT.APP.{pop_app}")
            moem.self_alter_mood_new_intent()
            log.data_collection("AUTONOMUS ACTIONS", "ROUTINE SUGGESTION", f"Routine suggestion accepted: {suggestion}")
        elif usr_feedback == "n":
            for app in flag_update:
                if suggestion == app:
                    ignored_apps[app] = "ignore"
                    scm.self_ignore_temp(suggestion)
                    mfl.flag_update("ignored_apps", ignored_apps)
                    pop_app = app
            flag_update.pop(pop_app)
            mfl.flag_update("apps_recently_used", flag_update)
            log.data_collection("AUTONOMUS ACTIONS", "ROUTINE SUGGESTION", f"Routine suggestion ignored: {suggestion}")
        mfl.flag_update("have_suggestion", False)
    except Exception as e:
        log.data_collection("AUTONOMUS ACTIONS", "ERROR", f"Error setting new routine: {e}")