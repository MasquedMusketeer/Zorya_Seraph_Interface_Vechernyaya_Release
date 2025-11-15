import os
import sys
import time
import importlib
import random as rnd
import threading as parallel
import Data.text_processing_module as tpm
import Data.audio_play_module as apm
import Data.memory_flags_loader as mfl
import Data.interpretation_engine as interpreter
import Data.system_control_module as scm
import Data.log_handler as log

main_loop_continuity = True
startup_errors = 0

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
#----------------------------------------------------------------set session ID
    if mfl_flag[1] != 0:
        print("Session ID could not be set due to memory load error.")
        print("Using fallback session ID.")
    else:
        sessionID =hex(mfl.flag_return("session_count"))
        log.session_setter(sessionID)
        mfl.flag_update("session_count", mfl.flag_return("session_count")+1)
        print("Session ID set to:", sessionID)
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

def audio_text_synchronizer(cathegory: str):
    valid_id_lines = apm.audio_index.get(cathegory, {}).keys()
    random_id = rnd.choice(list(valid_id_lines))
    greeting_lines = tpm.clean_text(int(random_id))
    if greeting_lines == list:
        for line in greeting_lines:
            print(line)
    else:
        print(greeting_lines)
    parallel.Thread(target=apm.play_line,args=(cathegory, random_id),daemon=True).start()

def respond_self_query(dummy_parameter):
    audio_text_synchronizer("HAPPY")

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
    if startup_errors == 0:
        print("All systems nominal.")
    else:
        print("Errors on execution,")
        print("refer to logs for details.")
    print("-------------------------------")
    log.data_collection("SYSTEM", "REPORT", f"talk_flag: {talk_flag},Current mood score: {mfl.flag_return('self_mood_score')},Operator mood score: {mfl.flag_return('operator_mood_score')},Startup errors: {startup_errors}")
    
    

    

def startup_sequence():
    load_assets()
    if mfl.flag_return("first_time") == True:
        header_load()
        first_startup()
        mfl.flag_update("first_time", False)
    else:
        header_load()
        audio_text_synchronizer("GREETING")

def shut_down_sequence(dummy_parameter):
    audio_text_synchronizer("BYE")
    log.data_collection("SYSTEM", "SHUTDOWN", "Shutting down Zorya...")
    time.sleep(7)
    global main_loop_continuity
    main_loop_continuity = False

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
        if action_function_name == "respond_self_query" or action_function_name == "shut_down_sequence" or action_function_name == "report_self_status":
            action_function(resolved_parameters)
        elif action_function_name == "set_talk_flag" and resolved_parameters == False:
            log.data_collection("ZORYA", "TALK", f"Executed {action_function_name}")
            audio_text_synchronizer("SILENT")
            action_function(resolved_parameters)
        elif action_function_name == "set_talk_flag" and resolved_parameters == True:
            log.data_collection("ZORYA", "TALK", f"Executed {action_function_name}")
            action_function(resolved_parameters)
            audio_text_synchronizer("TALK")
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
        