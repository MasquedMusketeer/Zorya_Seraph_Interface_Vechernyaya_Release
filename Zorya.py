import os
import sys
import time
import psutil
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

main_loop_continuity = True
startup_errors = 0

def memory_usage():
    process = psutil.Process(os.getpid())
    mem_bytes = process.memory_info().rss
    mem_kb = mem_bytes / 1024
    return(f"Memory usage: {mem_kb:.2f} KB")

def load_assets():
    error_catch = 0
    error_flags = []
    print("Starting up Zorya...")
#----------------------------------------------------------------memory flags load
    mfl_flag = mfl.memory_load()
    if mfl_flag[1] != 0:
        error_flags.append(mfl_flag[0])
        print(f"Error loading memory flags: {mfl_flag[0]}")
        error_catch += 1
    else:
        print("Memory flags loaded...")
#----------------------------------------------------------------text files load
    tpm_flag = tpm.load_text_file()
    if tpm_flag[1] != 0:
        error_flags.append(tpm_flag[0])
        print(f"Error loading text files: {tpm_flag[0]}")
        error_catch += 1
    else:
        print("Text files loaded...")
#----------------------------------------------------------------audio files load
    apm_flag = apm.load_audio_index()
    if apm_flag[1] != 0:
        error_flags.append(apm_flag[0])
        print(f"Error loading audio files: {apm_flag[0]}")
        error_catch += 1
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
#----------------------------------------------------------------set session ID
    if mfl_flag[1] != 0:
        print("Session ID could not be set due to memory load error.")
        print("Using fallback session ID.")
    else:
        sessionID =hex(mfl.flag_return("session_count"))
        log.session_setter(sessionID)
        mfl.flag_update("session_count", mfl.flag_return("session_count")+1)
        print("Session ID set to:", sessionID)
#-----------------------------------------------------------------memory usage
    print(memory_usage())
#-----------------------------------------------------------------log size analisys
    log_size = log.count_log_lines()
    print(f"Current log size: {log_size} lines.")
    mfl.flag_update("log_size", log_size)
#-----------------------------------------------------------------final report
    if error_catch != 0:
        global startup_errors
        startup_errors += error_catch
        print("Errors occurred during startup. Refer to logs for details.")
        log.data_collection("SYSTEM", "STARTUP", f"Startup completed with {error_catch} errors.")
        for error in error_flags:
            log.data_collection("SYSTEM", "STARTUP", f"Startup error: {error}")
    else:
        print("All assets loaded successfully.")
        log.data_collection("SYSTEM", "STARTUP", "Startup completed successfully.")
        apm.play_line("START_UP", "0")
    usr_input = input("Press Enter to continue...")

def startup_apps_on_power_on():
    startup_apps = mfl.flag_return("apps_expected_at_start")
    boot_time = psutil.boot_time()
    uptime_seconds = time.time() - boot_time
    if uptime_seconds < 300:
        for app in startup_apps:
            try:
                scm.call_program(app)
            except Exception as e:
                log.data_collection("SYSTEM", "ERROR", f"Error calling program {app} at startup: {e}")

def header_load():
    os.system('cls' if os.name == 'nt' else 'clear')
    with open(os.path.join(os.path.dirname(__file__), "Data","text_files",'interface.txt'), 'r', encoding='utf-8') as header:
        for line in header:
            print(line.strip("\n"))

def first_startup():
    text_lines = tpm.clean_text(401)
    for x in text_lines:
        print(x)
    apm.play_line("FIRST_RUN", "1")
    
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
        if app_name not in scm.program_paths:
            log.data_collection("STARTUP APP", "SET STARTUP APP", f"No program found, setting new program path for {app_name}")
            print(f"Program {app_name} not found.")
            print("Initializing new program registration.")
            scm.set_program_path("dummy_parameter")
        mfl.flag_update("apps_expected_at_start", app_name)
        log.data_collection("STARTUP APP", "SET STARTUP APP", f"New program path set for {app_name}")
    except Exception as e:
        log.data_collection("STARTUP APP", "SET STARTUP APP ERROR", f"Error setting new program path for {app_name}: {e}")

def audio_text_synchronizer(cathegory: str):
    mfl.flag_update("last_phrase_type",cathegory)
    valid_id_lines = apm.audio_index.get(cathegory, {}).keys()
    random_id = rnd.choice(list(valid_id_lines))
    mfl.flag_update("last_phrase_index", random_id)
    dialogue_lines = tpm.clean_text(int(random_id))
    if dialogue_lines[0] == "MULTILINE":
        dialogue_lines.pop(0)
        parallel.Thread(target=apm.play_line,args=(cathegory, random_id),daemon=True).start()
        for line in dialogue_lines:
            print(line)
        print("")
    else:
        print(dialogue_lines)
    parallel.Thread(target=apm.play_line,args=(cathegory, random_id),daemon=True).start()

def respond_self_query(dummy_parameter):
    audio_text_synchronizer("HAPPY")

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
    print(f"Current mood score: {mfl.flag_return('self_mood_score')}")
    print(f"Operator mood score: {mfl.flag_return('operator_mood_score')}")
    print(memory_usage())
    if startup_errors == 0:
        print("All systems nominal.")
    else:
        print("Errors on execution,")
        print("refer to logs for details.")
    print("-------------------------------")
    print("")
    log.data_collection("SYSTEM", "REPORT", f"talk_flag: {talk_flag},Current mood score: {mfl.flag_return('self_mood_score')},Operator mood score: {mfl.flag_return('operator_mood_score')},Startup errors: {startup_errors}")

def startup_sequence():
    load_assets()
    if mfl.flag_return("first_time") == True:
        header_load()
        first_startup()
        mfl.flag_update("first_time", False)
    else:
        header_load()
        try:
            correct_shut_down = mfl.flag_return("correct_power_off")
            if correct_shut_down == True:
                mfl.flag_update("correct_power_off", False)
                audio_text_synchronizer("GREETING")
            elif correct_shut_down == False:
                log.data_collection("SYSTEM", "ERROR", f"Abrupt shutdown detected at session: {hex(int(mfl.flag_return("session_count")) - 2)}.")
                audio_text_synchronizer("FAILED_SHUTDOWN")
        except Exception as e:
            log.data_collection("SYSTEM", "ERROR", f"Error during startup sequence: {e}")
            audio_text_synchronizer("ERROR")
        startup_apps_on_power_on()

def shut_down_sequence(dummy_parameter):
    audio_text_synchronizer("BYE")
    interpreter.save_new_routine()
    mfl.flag_update("correct_power_off", True)
    last_time_on = time.strftime("%Y-%m-%d %H:%M:%S")
    mfl.flag_update("last_hour_uptime", last_time_on)
    log.data_collection("SYSTEM", "SHUTDOWN", "Shutting down Zorya...")
    log_size = mfl.flag_return("log_size")
    if log_size > 15000:
        log.log_clean()
        mfl.flag_update("log_size", 3)
    time.sleep(7)
    global main_loop_continuity
    main_loop_continuity = False

def update_self_intent_mapping(dummy_parameter):
    interpreter.save_new_routine()
    interpreter.flush_memory()
    interpreter.intent_map_load()
    log.data_collection("SYSTEM", "UPDATE INTENT MAP", "Intent map updated.")
    print("Intent map updated.")
    print("")

def self_query_intent_report(dummy_parameter):
    print("-------------------------------")
    print(f"    My current intents: {len(interpreter.intent_map)}")
    print("-------------------------------")
    print("")

def self_recent_log_report(dummy_parameter):
    recent_logs = log.show_recent_logs()
    for logs in recent_logs:
        if logs != "":
            print(logs)
    print("")

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
        response_exception = ["respond_self_query","shut_down_sequence","report_self_status","respond_self_features"]
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
#---------------------------------------------------------------------------------------General execution
        elif action_function_name == "execute_command":
            audio_text_synchronizer("EXECUTION")
            action_function(resolved_parameters)
            log.data_collection("ZORYA", "EXECUTE", f"Executed {action_function_name}.{resolved_parameters}")
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
print("")

while main_loop_continuity == True:
    usr_input = input("You: ")
    phrase_contract = interpreter.interpret_tokens(usr_input)
    if phrase_contract is not None:
        (intent_id, action_module_name, action_function_name, resolved_parameters) = phrase_contract
        execute_action(intent_id, action_module_name, action_function_name, resolved_parameters)
    else:
        audio_text_synchronizer("ERROR")
        