from . import log_handler as log
from . import memory_flags_loader as mfl
from . import system_control_module as scm
from . import interpretation_engine as interpreter
from . import routine_builder_module as rbm
from . import mood_engine_module as moem
from. import system_watcher_module as swm
from . import response_handler as rph
import time
import random as rnd

#_________________________________________________________________________________________________________________________
#____________________________________________________ROUTINE HANDLER______________________________________________________
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
                suggested_apps_in_queue.append(app)
                mfl.flag_update("suggestion_apps", suggested_apps_in_queue)
        return None
        
    except Exception as e:
        log.data_collection("AUTONOMUS ACTIONS", "ERROR", f"Error checking routine frequent: {e}")
        return None
def set_new_routine(suggestion, usr_feedback, name_alias, is_suggestion_empty):
    try:
        flag_update = mfl.flag_return("apps_recently_used")
        silenced_apps = mfl.flag_return("silenced_apps")
        ignored_apps = mfl.flag_return("ignored_apps")
        pop_app = ""
        if usr_feedback == "y":
            scm.self_temp_to_disk(suggestion)
            rbm.self_build_routine(f"INTENT_OPEN_{name_alias.upper()}",f"open the app {name_alias}",["ACTION.OPEN",f"OBJECT.APP.{name_alias}"],"system_control_module","call_program",suggestion)
            for app in flag_update:
                if suggestion == app:
                    silenced_apps[app] = "silence"
                    mfl.flag_update("silenced_apps", silenced_apps)
                    pop_app = app
            flag_update.pop(pop_app)
            mfl.flag_update("apps_recently_used", flag_update)
            if pop_app == name_alias:
                interpreter._save_vocabulary(f"OBJECT.APP.{pop_app}")
            else:
                interpreter._save_vocabulary(f"OBJECT.APP.{name_alias}")
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
        
        if not is_suggestion_empty:
            mfl.flag_update("have_suggestion", False)
            log.data_collection("AUTONOMUS ACTIONS", "ROUTINE SUGGESTION", "No more suggestions available, updated sugestion flag.")
        elif is_suggestion_empty:
            log.data_collection("AUTONOMUS ACTIONS", "ROUTINE SUGGESTION", "More suggestions available, kept suggestion flag value.")
    except Exception as e:
        log.data_collection("AUTONOMUS ACTIONS", "ERROR", f"Error setting new routine: {e}")
#_________________________________________________________________________________________________________________________
#_________________________________________________RESOURCE NOTIFICATOR____________________________________________________
noification_queue = []

def watch_resource_high_usage(stop_event):
    cpu_usage_alert_tick_count = 0
    memory_usage_alert_tick_count = 0
    trash_usage_tick_count = 0
    cpu_alert_active = False
    ram_alert_active = False
    download_alert_active = False
    disk_alert_set = set()
    log_interval = 90
    
    def notify_usage(label, usage):
            log.data_collection("AUTONOMUS ACTIONS", "RESOURCE HIGH USAGE", f"High {label} usage detected: {usage}")
            noification_queue.append((f"High {label} usage detected: {usage}", "⚠️ WARNING"))
            moem.self_alter_mood_feeling_useful()
    
    while not stop_event.is_set():
        time.sleep(10)
        system_resources = swm.return_system_info()
        trash_bin_size = swm.get_trash_size()
        download_file_count = swm.get_download_file_count()
        cpu_usage = system_resources["cpu_usage"]
        memory_usage = system_resources["memory_usage"]
        disk_usage = system_resources["disk_usage"]
        system_alert_mute_flags = mfl.flag_return("system_alert_notification_mute_flag")
        system_alert_thresholds = mfl.flag_return("system_alert_threshold_flag")
        if log_interval == 0:
            log_interval = 90
            log.data_collection("AUTONOMUS ACTIONS", "RESOURCE USAGE", f"CPU: {cpu_usage}, RAM: {memory_usage}, DISK: {disk_usage}")

#_____________________________________________DISK ALERT__________________________________________
        for disk, info in disk_usage.items():
            if info["percentage"] > system_alert_thresholds["disk"] and not system_alert_mute_flags["disk"] and disk not in disk_alert_set:
                notify_usage("DISK", f"{disk}: {info['percentage']}%")
                disk_alert_set.add(disk)
            elif info["percentage"] < system_alert_thresholds["disk"] and disk in disk_alert_set:
                disk_alert_set.discard(disk)
                
#____________________________________________CPU ALERT____________________________________________            
        if cpu_usage > system_alert_thresholds["cpu"]:
            cpu_usage_alert_tick_count += 1
            if cpu_usage_alert_tick_count > 6 and not cpu_alert_active:
                if not system_alert_mute_flags["cpu"]:
                    notify_usage("CPU", f"{cpu_usage}%")
                cpu_alert_active = True
        else:
            cpu_usage_alert_tick_count = 0
            cpu_alert_active = False
#____________________________________________RAM ALERT____________________________________________
        if memory_usage > system_alert_thresholds["ram"]:
            memory_usage_alert_tick_count += 1
            if memory_usage_alert_tick_count > 6 and not ram_alert_active:
                if not system_alert_mute_flags["ram"]:
                    notify_usage("RAM", f"{memory_usage}%")
                ram_alert_active = True
        else:
            memory_usage_alert_tick_count = 0
            ram_alert_active = False
#____________________________________________TRASH ALERT___________________________________________
        if trash_bin_size is not None and trash_bin_size > system_alert_thresholds["trash"] and trash_bin_size < 10240:
            trash_usage_tick_count += 1
            if trash_usage_tick_count > 480:
                if not system_alert_mute_flags["trash"]:
                    notify_usage("TRASH", f"{round((trash_bin_size / 1024),2)} GB")
                trash_usage_tick_count = 0
        elif trash_bin_size is not None and trash_bin_size >= 10240:
            if trash_usage_tick_count > 180:
                rph.audio_text_synchronizer("TRASH")
                trash_usage_tick_count = 0
#__________________________________________DOWNLOAD ALERT__________________________________________
        if download_file_count is not None and download_file_count > system_alert_thresholds["download"] and download_alert_active == False:
            notify_usage("DOWNLOAD", f"{download_file_count} files found on Download folder.")
            download_alert_active = True
        elif download_file_count is not None and download_file_count <= system_alert_thresholds["download"]:
            download_alert_active = False
#__________________________________________________________________________________________________
        log_interval -= 1
        if noification_queue:
            send_message = noification_queue.pop(0)
            log.Zorya_notifier(*send_message)

def kill_high_usage_processes(stop_event):  #--------------WIP
    return None

def kill_unwanted_running_apps(stop_event):
    try:
        already_alerted_apps = []
        log_data_frequency_counter = 10
        while not stop_event.is_set():
            unwanted_apps = swm.get_warning_level_running_apps("black_list", log_data_frequency_counter)
            if unwanted_apps:
                for app in unwanted_apps:
                    scm.self_kill_program(app)
                    if app not in already_alerted_apps:
                         log.Zorya_notifier(f"Unwanted app detected and terminated: {app}, class: black_list", "⚠️ WARNING")
                         already_alerted_apps.append(app)
                log.data_collection("AUTONOMUS ACTIONS", "KILL UNWANTED APPS", f"Killed unwanted apps: {unwanted_apps}")
            else:
                pass
            log_data_frequency_counter -= 1
            if log_data_frequency_counter == 0:
                log_data_frequency_counter = 10
            time.sleep(60)
    except Exception as e:
        log.data_collection("AUTONOMUS ACTIONS", "ERROR", f"Error killing unwanted apps: {e}")
#_________________________________________________________________________________________________________________________
#________________________________________________RANDOM BANTER HANDLER____________________________________________________
BANTER_CATEGORY = ["BANTER", "SASS"]

def autonomus_banter_handler(stop_event):
    try:
        while not stop_event.is_set():
            banter_delay = rnd.randint(1800, 3600)
            banter_cat_choice = rnd.choice(BANTER_CATEGORY)
            time.sleep(banter_delay)
            rph.audio_text_synchronizer(banter_cat_choice)
    except Exception as e:
        log.data_collection("AUTONOMUS ACTIONS", "ERROR", f"Error in autonomus banter handler: {e}")
#_________________________________________________________________________________________________________________________
#___________________________________________AUTONOMOUS JOKE DICT SELECTOR_________________________________________________
###WIP