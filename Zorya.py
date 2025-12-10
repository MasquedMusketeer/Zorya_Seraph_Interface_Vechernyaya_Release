import os
import sys
import time
import psutil
import datetime
import importlib
import random as rnd
import threading as parallel
import Data.text_processing_module as tpm
import Data.audio_play_module as apm
import Data.memory_flags_loader as mfl
import Data.interpretation_engine as interpreter
import Data.system_control_module as scm
import Data.log_handler as log
import Data.routine_builder_module as rbm
import Data.pattern_recognition_module as prm
import Data.autonomus_actions_module as aam
import Data.putty_manager_module as pmm
import Data.mood_engine_module as moem
import Data.command_runner as cmr

main_loop_continuity = True
startup_errors = 0

def memory_usage():
    process = psutil.Process(os.getpid())
    mem_bytes = process.memory_info().rss
    mem_kb = mem_bytes / 1024
    return(f"Memory usage: {mem_kb:.2f} KB")

def load_assets():
    error_catch = 0
    essential_modules_error = 0
    error_flags = []
    print("Starting up Zorya...")
#----------------------------------------------------------------memory flags load
    mfl_flag = mfl.memory_load()
    if mfl_flag[1] != 0:
        error_flags.append(mfl_flag[0])
        print(f"Error loading memory flags: {mfl_flag[0]}")
        error_catch += 1
        essential_modules_error += 1
    else:
        print("Memory flags loaded...")
#----------------------------------------------------------------text files load
    tpm_flag = tpm.load_text_file()
    if tpm_flag[1] != 0:
        error_flags.append(tpm_flag[0])
        print(f"Error loading text files: {tpm_flag[0]}")
        error_catch += 1
        essential_modules_error += 1
    else:
        print("Text files loaded...")
#----------------------------------------------------------------audio files load
    apm_flag = apm.load_audio_index()
    if apm_flag[1] != 0:
        error_flags.append(apm_flag[0])
        print(f"Error loading audio files: {apm_flag[0]}")
        error_catch += 1
        essential_modules_error += 1
    else:
        print("Audio files loaded...")
#----------------------------------------------------------------vocabulary load
    vocabulary_flag = interpreter.vocabulary_load()
    if vocabulary_flag[1] != 0:
        error_flags.append(vocabulary_flag[0])
        print(f"Error loading vocabulary: {vocabulary_flag[0]}")
        error_catch += 1
    else:
        print("Vocabulary loaded...")
#----------------------------------------------------------------intent map load
    intent_map_flag = interpreter.intent_map_load()
    if intent_map_flag[1] != 0:
        error_flags.append(intent_map_flag[0])
        print(f"Error loading intent map: {intent_map_flag[0]}")
        error_catch += 1
    else:
        print("Intent map loaded...")
#----------------------------------------------------------------program paths load
    program_path_flag = scm.load_program_paths()
    if program_path_flag[1] != 0:
        error_flags.append(program_path_flag[0])
        print(f"Error loading program paths: {program_path_flag[0]}")
        error_catch += 1
    else:
        print("Program paths loaded...")
#----------------------------------------------------------------folder paths load
    folder_path_flag = scm.load_folder_paths()
    if folder_path_flag[1] != 0:
        error_flags.append(folder_path_flag[0])
        print(f"Error loading folder paths: {folder_path_flag[0]}")
        error_catch += 1
    else:
        print("Folder paths loaded...")
#----------------------------------------------------------------routine buffer load
    routine_buffer_flag = rbm.load_short_memory()
    if routine_buffer_flag[1] != 0:
        error_flags.append(routine_buffer_flag[0])
        print(f"Error loading routine buffer: {routine_buffer_flag[0]}")
        error_catch += 1
    else:
        print("Short memory loaded...")
#----------------------------------------------------------------ssh profile load
    ssh_flag = pmm.load_ssh_profile_dict()
    if ssh_flag[1] != 0:
        error_flags.append(ssh_flag[0])
        print(f"Error loading ssh profiles: {ssh_flag[0]}")
        error_catch += 1
    else:
        print("SSH profiles loaded...")
#----------------------------------------------------------------set session ID
    if mfl_flag[1] != 0:
        print("Session ID could not be set due to memory load error.")
        print("Using fallback session ID.")
    else:
        sessionID =hex(mfl.flag_return("session_count"))
        log.session_setter(sessionID)
        mfl.flag_update("session_count", mfl.flag_return("session_count")+1)
        print("Session ID set to:", sessionID.upper().replace("0X", "$"))
#-----------------------------------------------------------------memory usage
    print(memory_usage())
#-----------------------------------------------------------------log size analisys
    log_size = log.count_log_lines()
    print(f"Current log size: {log_size} lines.")
    mfl.flag_update("log_size", log_size)
#-----------------------------------------------------------------final report
    if error_catch != 0 and essential_modules_error == 0:
        global startup_errors
        startup_errors += error_catch
        print("Errors occurred during startup. Refer to logs for details.")
        log.data_collection("ZORYA", "ERROR", f"Startup completed with {error_catch} errors.")
        for error in error_flags:
            log.data_collection("ZORYA", "ERROR", f"Startup error: {error}")
    elif essential_modules_error != 0:
        print("\033[91mCatastrophic errors occurred during startup. Refer to logs for details.\033[0m")
        log.data_collection("ZORYA", "ERROR", f"Startup completed with {essential_modules_error} critical errors.")
        time.sleep(5)
        sys.exit(1)
    else:
        print("All assets loaded successfully.")
        log.data_collection("ZORYA", "STARTUP", "Startup completed successfully.")
        apm.play_line("START_UP", "0")
    usr_input = input("Press Enter to continue...")

def startup_apps_on_power_on():
    startup_apps = mfl.flag_return("apps_expected_at_start")
    current_running_apps = prm._get_visible_apps()
    try:
        for s_app in startup_apps:
            app_is_running = any(s_app.lower() in r.lower() for r in current_running_apps)
            if not app_is_running:
                scm.call_program(s_app)
                log.data_collection("ZORYA", "STARTUP APP", f"Started {s_app} at startup.")
            else:
                log.data_collection("ZORYA", "STARTUP APP", f"{s_app} is already running.")
    except Exception as e:
        log.data_collection("ZORYA", "ERROR", f"Error starting up apps: {e}")

def header_load():
    os.system('cls' if os.name == 'nt' else 'clear')
    header = tpm.header_return()
    for line in header:
        print(line.strip("\n"))

def first_startup():
    audio_text_synchronizer("FIRST_TIME")
    
def protocol_matrix(dummy_parameter):
    print("-------------------------------")
    print("   Protocol matrix engaged")
    print("-------------------------------")
    print("")
    time.sleep(0.5)
    print("synchronizing cipher blocks...")
    time.sleep(0.5)
    
    counter = 250
    while counter > 0:
        counter_line = 32
        line = ""
        while counter_line > 0:
            number = rnd.randint(0, 1)
            line += str(number)
            counter_line -= 1
        print(line)
        sleep_time = rnd.randint(1, 7)
        sleep_time = sleep_time / 100
        time.sleep(sleep_time)
        counter -= 1
    print("")
    print("Protocol matrix finished.")
    
def set_new_startup_app(dummy_parameter):
    try:
        app_name = input("Enter the name of the program you want to run at startup: ")
        app_name = app_name.lower()
        if app_name not in scm.program_paths:
            log.data_collection("ZORYA", "SET STARTUP APP", f"No program found, setting new program path for {app_name}")
            print(f"Program {app_name} not found.")
            print("Initializing new program registration.")
            scm.set_program_path("dummy_parameter")
        mfl.flag_update("apps_expected_at_start", app_name)
        mfl.save_ram_flags()
        log.data_collection("ZORYA", "SET STARTUP APP", f"New program path set for {app_name}")
    except Exception as e:
        log.data_collection("ZORYA", "ERROR", f"Error setting new program path for {app_name}: {e}")

def audio_text_synchronizer(category: str):
    mfl.flag_update("last_phrase_type",category)
    valid_id_lines = apm.audio_index.get(category, {}).keys()
    random_id = rnd.choice(list(valid_id_lines))
    mfl.flag_update("last_phrase_index", random_id)
    mfl.save_ram_flags()
    dialogue_lines = tpm.clean_text(category, str(random_id))
    if dialogue_lines[0] == "MULTILINE":
        dialogue_lines.pop(0)
        parallel.Thread(target=apm.play_line,args=(category, random_id),daemon=True).start()
        for line in dialogue_lines:
            print(line)
    else:
        print(dialogue_lines.strip("\n"))
    parallel.Thread(target=apm.play_line,args=(category, random_id),daemon=True).start()
#-------------------------------------------------------------------------------------------self execution-----------------------------

def self_backup_memory_folder():
    memory_folder = os.path.join(os.path.dirname(__file__), "Data", "Long_term_memory")
    appdata = os.getenv("APPDATA")
    backup_folder = os.path.join(appdata, "Zorya", "Memory_backup")
    if not os.path.exists(backup_folder):
        os.makedirs(backup_folder)
    cmr.self_silent_command(f'robocopy "{memory_folder}" "{backup_folder}" /E')
    log.data_collection("ZORYA", "BACKUP", "Memory folder backed up.")
    mfl.flag_update("make_backup", False)
    mfl.flag_update("last_backup_session_ID",log.sessionID_return())

def self_restore_backup():
    memory_folder = os.path.join(os.path.dirname(__file__), "Data", "Long_term_memory")
    appdata = os.getenv("APPDATA")
    backup_folder = os.path.join(appdata, "Zorya", "Memory_backup")
    if not os.path.exists(backup_folder):
        os.makedirs(backup_folder)
    cmr.self_silent_command(f'robocopy "{backup_folder}" "{memory_folder}" /E')
    log.data_collection("ZORYA", "RESTORE", "Memory folder restored.")
    mfl.flag_update("restore_backup", False)

def respond_self_query(dummy_parameter):
    audio_text_synchronizer("HAPPY")

def self_tell_joke(dummy_param):
    audio_text_synchronizer("JOKE")
    moem.self_alter_mood_tell_joke()

def self_save_new_vocab(dummy_param):
    try:
        audio_text_synchronizer("VOCAB")
        print("Zorya: What is the new word?")
        new_word = input("You: ").strip(" ").lower()
        if not new_word:
            print("Zorya: You dont expect me to believe your 'word' exists, right?")
            return
        print("Zorya: Fine. What category does this alleged word belong to?")
        print("Zorya: Here are the ones I *already* know, not that you checked before asking:")
        all_categories = interpreter.get_all_vocab_classifications()
        for cat in all_categories:
            print(cat)
        category = input("You: ")
        category = category.strip().upper()
        if "." not in category:
            print("Zorya: That's not a category. That's... whatever that is. Try again when you're coherent.")
            return
        vocab_param = f"{category}.{new_word}"
        interpreter.save_new_vocabulary(vocab_param)
        print("Zorya: Well, congrats, at least you didn't break me this time.")
        moem.self_alter_mood_new_words()
    except Exception as e:
        log.data_collection("SYSTEM", "ERROR", f"Error saving new vocabulary: {e}")
        print("Zorya: I'm not sure what happened, but definetly wasn't supposed to. Try again with the brain on.")

def respond_self_features(dummy_parameter):
    audio_text_synchronizer("FEATURES")

def respond_time_query(dummy_parameter):
    print("-------------------------------")
    print(f"Current time: {time.strftime('%H:%M:%S')}")
    print("-------------------------------")
    print("")

def report_self_status(dummy_parameter):
    print("-------------------------------")
    print("    Zorya current status")
    print("-------------------------------")
    print(f"Session ID: {log.sessionID_return()}")
    print(f"Startup errors: {startup_errors}")
    talk_flag = apm.return_talk_flag()
    if talk_flag == True:
        print("Zorya is set to talk.")
    else:
        print("Zorya is set to silent.")
    print("Current mood score: ")
    self_mood = mfl.flag_return('self_mood_score')
    for key in self_mood:
        print(f"{key}: {self_mood[key]}")
    print(f"Operator mood score: {mfl.flag_return('operator_mood_score')}")
    print(memory_usage())
    if startup_errors == 0:
        print("All systems nominal.")
    else:
        print("Errors on execution,")
        print("refer to logs for details.")
    print("-------------------------------")
    log.data_collection("ZORYA", "REPORT", f"talk_flag: {talk_flag},Current mood score: {mfl.flag_return('self_mood_score')},Operator mood score: {mfl.flag_return('operator_mood_score')},Startup errors: {startup_errors}")

def self_query_intent_report(dummy_parameter):
    print("-------------------------------")
    print(f"    My current intents: {len(interpreter.intent_map)}")
    print("-------------------------------")

def self_recent_log_report(dummy_parameter):
    recent_logs = log.show_recent_logs()
    for logs in recent_logs:
        if logs != "":
            print(logs)
            
def self_user_tracking_decrement_thread():
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
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def startup_sequence():
    load_assets()
    if mfl.flag_return("first_time") == True:
        header_load()
        first_startup()
        mfl.flag_update("first_time", False)
    else:
        header_load()
        try:
            have_suggestion = mfl.flag_return("have_suggestion")
            correct_shut_down = mfl.flag_return("correct_power_off")
            if have_suggestion == True:
                suggest_new_app_routine()
            elif correct_shut_down == True:
                mfl.flag_update("correct_power_off", False)
                audio_text_synchronizer("GREETING")
                moem.self_alter_mood_successful_shutdown()
            elif correct_shut_down == False:
                log.data_collection("ZORYA", "ERROR", f"Abrupt shutdown detected at session: {hex(int(mfl.flag_return("session_count")) - 2)}.")
                audio_text_synchronizer("FAILED_SHUTDOWN")
                moem.self_alter_mood_failed_shutdown()
        except Exception as e:
            log.data_collection("ZORYA", "ERROR", f"Error during startup sequence: {e}")
            audio_text_synchronizer("ERROR")
        try:
            startup_apps_on_power_on()
        except Exception as e:
            log.data_collection("ZORYA", "ERROR", f"Error during startup apps on power on: {e}")
        poweron_time = time.strftime("%Y-%m-%d %H:%M:%S")
        mfl.flag_update("last_hour_uptime", poweron_time)
        mfl.save_ram_flags()
        parallel.Thread(target=update_frequently_used_apps, args=("dummy_parameter",), daemon=True).start()
        parallel.Thread(target=self_user_tracking_decrement_thread, daemon=True).start()
        log.data_collection("ZORYA", "STARTUP", "Separate processing threads started...")
        log.data_collection("ZORYA", "STARTUP", "Startup sequence completed with no errors.")

def shut_down_sequence(dummy_parameter):
    try:
        audio_text_synchronizer("BYE")
        interpreter.save_new_routine()
        mfl.flag_update("correct_power_off", True)
        last_time_on = time.strftime("%Y-%m-%d %H:%M:%S")
        mfl.flag_update("last_hour_downtime", last_time_on)
        last_poweron_time = mfl.flag_return("last_hour_uptime")
        last_poweron_time = datetime.datetime.strptime(last_poweron_time, "%Y-%m-%d %H:%M:%S")
        last_poweroff_time = datetime.datetime.strptime(last_time_on, "%Y-%m-%d %H:%M:%S")
        total_uptime = last_poweroff_time - last_poweron_time
        total_uptime = round((total_uptime.total_seconds()/60), 2)
        mfl.flag_update("last_uptime_count", total_uptime)
        log_size = mfl.flag_return("log_size")
        if log_size > 15000:
            log.log_clean()
            mfl.flag_update("log_size", 3)
        backup_flag = mfl.flag_return("make_backup")
        restore_backup_flag = mfl.flag_return("restore_backup")
        if backup_flag == True:
            self_backup_memory_folder()
        if restore_backup_flag == True:
            self_restore_backup()
        mfl.save_ram_flags()
        log.data_collection("ZORYA", "SHUTDOWN", "Shutting down Zorya...")
        time.sleep(7)
        global main_loop_continuity
        main_loop_continuity = False
    except Exception as e:
        log.data_collection("ZORYA", "ERROR", f"Error during shutdown sequence: {e}")

def update_self_intent_mapping(dummy_parameter):
    interpreter.save_new_routine()
    interpreter.flush_memory()
    interpreter.intent_map_load()
    log.data_collection("ZORYA", "UPDATE INTENT MAP", "Intent map updated.")
    print("Intent map updated.")

def backup_handler(backup_indicator):
    try:
        if backup_indicator == "BACKUP":
            mfl.flag_update("make_backup", True)
        elif backup_indicator == "RESTORE":
            mfl.flag_update("restore_backup", True)
    except Exception as e:
        log.data_collection("ZORYA", "ERROR", f"Error handling backup: {e}")

def update_frequently_used_apps(dummy_parameter):
    degradation_counter = 2
    while True:
        try:
            prm.query_most_used_apps()
            aam.is_routine_frequent()
            unknown_apps = mfl.return_programs_not_known()
            open_apps = prm._get_visible_apps()
            for app in unknown_apps:
                if app in open_apps:
                    app_path = prm.get_exe_path_from_name(app)
                    if app_path != None:
                        scm.self_set_program_path(app, app_path)
            if degradation_counter == 0:
                prm.used_apps_score_degradation()
                degradation_counter += 3
            time.sleep(300)
            degradation_counter -= 1
            mfl.save_ram_flags()
        except Exception as e:
            log.data_collection("ZORYA", "ERROR", f"Error updating frequently used apps: {e}")

def suggest_new_app_routine():
    try:
        suggestion = mfl.flag_return("suggestion_apps")
        suggested_app = suggestion.pop(0)
        if suggested_app != None:
            audio_text_synchronizer("SUGGESTION")
            print(f"Routine suggestion: {suggested_app}"," (y/n)")
            usr_feedback = input("You: ").lower()
            aam.set_new_routine(suggested_app, usr_feedback)
            log.data_collection("ZORYA", "ROUTINE SUGGESTION", f"Routine suggestion: {suggested_app}, User feedback: {usr_feedback}")
    except Exception as e:
        log.data_collection("ZORYA", "ERROR", f"Error suggesting new app routine: {e}")

def execute_action(intent_id, action_module_name, action_function_name, resolved_parameters):
    target_module = None
#----------------------------------------------------------------------------Target is a function within this file    
    if action_module_name == 'Zorya':
        target_module = sys.modules[__name__]
#----------------------------------------------------------------------------Target is a function outside this file
    else:
        try:
            target_module = importlib.import_module(f"Data.{action_module_name}")
        except ImportError:
            audio_text_synchronizer("ERROR")
            log.data_collection("ZORYA", "ERROR", f"Module not found: {action_module_name}")
            return
#--------------------------------------------------------------------------------------Find and execute the function
    try:
        action_function = getattr(target_module, action_function_name)
#--------------------------------------------------------------------------------------Exceptions to general execution
        response_exception = [
            
            "respond_self_query",
            "shut_down_sequence",
            "report_self_status",
            "respond_self_features",
            "self_tell_joke",
            "self_save_new_vocab"
            
            ]
        if action_function_name in response_exception :
            action_function(resolved_parameters)
        elif action_function_name == "set_talk_flag" and resolved_parameters == False:
            log.data_collection("ZORYA", "TALK", f"Executed {action_function_name}")
            audio_text_synchronizer("SILENT")
            action_function(resolved_parameters)
        elif action_function_name == "set_talk_flag" and resolved_parameters == True:
            log.data_collection("ZORYA", "TALK", f"Executed {action_function_name}")
            action_function(resolved_parameters)
            audio_text_synchronizer("TALK")
        elif action_module_name == "debug_module":
            audio_text_synchronizer("DEBUG")
            action_function(resolved_parameters)
#---------------------------------------------------------------------------------------General execution
        elif action_function_name == "execute_command":
            audio_text_synchronizer("EXECUTION")
            action_function(resolved_parameters)
            log.data_collection("ZORYA", "EXECUTE", f"Executed {action_function_name}.{resolved_parameters}")
        elif "INTENT_SYSTEM_OVERRIDE" in intent_id:
            audio_text_synchronizer("DEBUG")
            action_function(resolved_parameters)
        else:
            audio_text_synchronizer("EXECUTION")
            action_function(resolved_parameters)
            log.data_collection("ZORYA", "EXECUTE", f"Executed {action_module_name}.{action_function_name}.{resolved_parameters}") 
    except AttributeError:
        audio_text_synchronizer("ERROR")
        log.data_collection("ZORYA", "ERROR", f"Function not found: {action_function_name} in {action_module_name}")
    except TypeError as e:
        audio_text_synchronizer("ERROR")
        log.data_collection("ZORYA", "ERROR", f"Parameter mismatch: {action_function_name} - {e}")
    except Exception as e:
        audio_text_synchronizer("ERROR")
        log.data_collection("ZORYA", "ERROR", f"Unexpected execution error: {e}")        
       
# Execute startup sequence
startup_sequence()

while main_loop_continuity == True:
    usr_input = input("You: ")
    self_user_tracking("increment")
    phrase_contract = interpreter.interpret_tokens(usr_input)
    if phrase_contract is not None:
        moem.self_alter_mood_successful_interpretation()
        (intent_id, action_module_name, action_function_name, resolved_parameters) = phrase_contract
        execute_action(intent_id, action_module_name, action_function_name, resolved_parameters)
    else:
        audio_text_synchronizer("ERROR")
        moem.self_alter_mood_failed_interpretation()
        