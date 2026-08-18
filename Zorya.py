import os, sys, time, datetime, importlib, threading as parallel, queue
from Data import (
    memory_flags_loader as mfl,
    backup_manager_module as bmm,
    response_handler as rph,
    system_control_module as scm,
    log_handler as log,
    audio_play_module as apm,
    text_processing_module as tpm,
    interpretation_engine as interpreter,
    system_watcher_module as swm,
    autonomus_actions_module as aam,
    pattern_recognition_module as prm,
    mood_engine_module as moem,
    bootstrapper as boot,
    status_dashboard_module as sdm,
    task_scheduler_module as tsm
)

command_queue = queue.Queue()
response_queue = queue.Queue()
main_loop_continuity = True
stop_event = parallel.Event()


#_________________________________________________________________________________________________________________________
#___________________________________________________STARTUP HELPER FUNCTIONS______________________________________________
def header_load():
        os.system('cls' if os.name == 'nt' else 'clear')
        header = tpm.header_return()
        for line in header:
            print(line.strip("\n"))

def first_startup():
    rph.audio_text_synchronizer("FIRST_RUN")

def startup_condition_check():
    try:
        have_suggestion = mfl.flag_return("have_suggestion")
        correct_shut_down = mfl.flag_return("correct_power_off")
        if have_suggestion == True:
            rph.audio_text_synchronizer("SUGGESTION")
            prm.suggest_new_app_routine()
        elif correct_shut_down == True:
            mfl.flag_update("correct_power_off", False)
            rph.audio_text_synchronizer("GREETING")
            moem.self_alter_mood_successful_shutdown()
        elif correct_shut_down == False:
            log.data_collection("ZORYA", "ERROR", f"Abrupt shutdown detected at session: {hex(int(mfl.flag_return("session_count")) - 2)}.")
            rph.audio_text_synchronizer("FAILED_SHUTDOWN")
            moem.self_alter_mood_failed_shutdown()
    except Exception as e:
        log.data_collection("ZORYA", "ERROR", f"Error during startup sequence: {e}")
        rph.audio_text_synchronizer("ERROR")
def startup_apps_launcher():
    try:
        scm.startup_apps_on_power_on(mfl.flag_return("apps_expected_at_start"),swm._get_visible_apps())
    except Exception as e:
        log.data_collection("ZORYA", "ERROR", f"Error during startup apps on power on: {e}")
    poweron_time = time.strftime("%Y-%m-%d %H:%M:%S")
    mfl.flag_update("last_hour_uptime", poweron_time)
    mfl.save_ram_flags()

def startup_threads_launcher():
    try:
#________________________________________SYSTEM READER THREADS___________________________________________________________
        parallel.Thread(target=prm.update_frequently_used_apps, args=(stop_event,), daemon=True).start()
        parallel.Thread(target=prm.self_user_tracking_decrement_thread,args=(stop_event,), daemon=True).start()
        parallel.Thread(target=aam.watch_resource_high_usage,args=(stop_event,), daemon=True).start()
        parallel.Thread(target=sdm.launch_dashboard, args=(stop_event, ), daemon=True).start()
        parallel.Thread(target=moem.degrade_joke_counter, args=(stop_event, ), daemon=True).start()
#_________________________________________SYSTEM WRITER THREADS__________________________________________________________
        parallel.Thread(target=swm.system_info_updater,args=(stop_event,), daemon=True).start()
        parallel.Thread(target=mfl.periodic_save_ram_flags_to_disk,args=(stop_event,), daemon=True).start()
#_________________________________________SYSTEM EXECUTION THREADS_______________________________________________________
        parallel.Thread(target=aam.kill_unwanted_running_apps,args=(stop_event,), daemon=True).start()
        parallel.Thread(target=aam.autonomus_banter_handler,args=(stop_event,), daemon=True).start()
        parallel.Thread(target=tsm.notify_due_schedules,args=(stop_event,), daemon=True).start()
        parallel.Thread(target=scm.run_program_from_queue, args=(stop_event, ), daemon=True).start()
#________________________________________________________________________________________________________________________
        log.data_collection("ZORYA", "STARTUP", "Separate processing threads started...")

    except Exception as e:
        log.data_collection("ZORYA", "ERROR", f"Error starting separate processing threads: {e}")
#_________________________________________________________________________________________________________________________
#___________________________________________SELF INFO TEXT OUTPUT_________________________________________________________
def self_info_response_handler(function):
    try:
        api_mode = mfl.flag_return("api_mode")
        target_module = importlib.import_module(f"Data.self_info_report_module")
        target_function = getattr(target_module, function)
        text = target_function(None)
        if api_mode:
            return text
        else:
            print(text)
    except Exception as e:
        log.data_collection("ZORYA", "ERROR", f"Error in self_info_response_handler: {e}")
#_________________________________________________________________________________________________________________________
#______________________________________________________API HANDLER________________________________________________________

def api_startup_sequence():
    boot.load_assets()
    startup_threads_launcher()
    parallel.Thread(target=_api_command_processor, args=(stop_event,), daemon=True).start()
    log.data_collection("ZORYA", "API MODE", "API mode started...")

def audio_text_hook(text,audio_file):
    text = tpm.clean_text(text)
    apm.play_line(audio_file)
    return text
    
def _api_command_processor(stop_event):
    while not stop_event.is_set():
        try:
            user_input = command_queue.get(timeout=1)
            result = ui_event_slot(user_input, False)
            response_queue.put(result)
        except queue.Empty:
            continue

def send_command(user_input):
    command_queue.put(user_input)
    return response_queue.get()

def ui_event_slot(user_input, system_info_flag):
    try:
        if not system_info_flag:
            prm.self_user_tracking("increment")
            phrase_contract = interpreter.interpret_tokens(user_input)
            if phrase_contract == None:
                phrase_contract = (None,None,None,None)
                moem.self_alter_mood_failed_interpretation()
            category = interpreter.map_intent_to_response(phrase_contract[0])
            rph._select_audio_text_line(category)
            api_return_output = {
                "intent":{
                    "id":phrase_contract[0],
                    "action_module":phrase_contract[1],
                    "action_function":phrase_contract[2],
                    "parameters":phrase_contract[3]
                },
                "response":{
                    "category":mfl.flag_return("last_phrase_type"),
                    "index":mfl.flag_return("last_phrase_index")
                },
                "mood":{
                    "self":mfl.flag_return("self_mood_score"),
                    "operator":mfl.flag_return("operator_mood_score")
                }
            }
        else:
            api_return_output = {
                "meta_data":{
                    "sessionID":log.sessionID_return(),
                    "self_mood":mfl.flag_return("self_mood_score"),
                    "have_suggestion":mfl.flag_return("have_suggestion"),
                    "correct_power_off":mfl.flag_return("correct_power_off"),
                    "apps_expected_at_start":mfl.flag_return("apps_expected_at_start")
                }
            }
        return api_return_output
    except Exception as e:
        log.data_collection("ZORYA", "ERROR", f"Error in UI event slot: {e}")
        return None
#_________________________________________________________________________________________________________________________
#_________________________________________________VOCABULARY HANDLER______________________________________________________
def self_save_new_vocab(_):
    rph.audio_text_synchronizer("VOCAB")
    interpreter.save_new_vocabulary(None)
#_________________________________________________________________________________________________________________________
#__________________________________________________QUESTION RESPONSE______________________________________________________
def respond_self_mood_query(_):
    try:
        mood_score = mfl.flag_return("self_mood_score")
        happy, neutral, sad = mood_score["happy"], mood_score["neutral"], mood_score["sad"]
        if happy > neutral and happy > sad:
            rph.audio_text_synchronizer("HAPPY")
        elif sad > neutral and sad > happy:
            rph.audio_text_synchronizer("SAD")
        else:
            rph.audio_text_synchronizer("MILD")
    except Exception as e:
        log.data_collection("ZORYA", "ERROR", f"Error responding to self mood query: {e}")
#________________________________________________________________________________________________________________________
#_________________________________________________SYSTEM START-STOP OP___________________________________________________
def _calculate_uptime():
    last_poweron = datetime.datetime.strptime(mfl.flag_return("last_hour_uptime"), "%Y-%m-%d %H:%M:%S")
    last_poweroff = datetime.datetime.strptime(time.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
    return round((last_poweroff - last_poweron).total_seconds() / 60, 2)

def _handle_backups():
    if mfl.flag_return("make_backup"):
        bmm.self_backup_memory_folder()
    if mfl.flag_return("restore_backup"):
        bmm.self_restore_backup()

def _cleanup_logs_if_needed():
    if mfl.flag_return("log_size") > 15000:
        log.log_clean()
        mfl.flag_update("log_size", 3)

def startup_sequence():
    log.data_collection("ZORYA", "STARTUP", "Starting Zorya...")
    boot.load_assets()
    if mfl.flag_return("first_time") == True:
        header_load()
        first_startup()
        mfl.flag_update("first_time", False)
    else:
        header_load()
        startup_condition_check()
        startup_apps_launcher()
        startup_threads_launcher()
        tsm.due_schedule_finder()
    log.data_collection("ZORYA", "STARTUP", "Startup sequence completed.")

def shut_down_sequence(_):
    try:
        api_mode = mfl.flag_return("api_mode")
        if not api_mode:
            rph.audio_text_synchronizer("BYE")
        
        interpreter.save_new_routine()
        mfl.flag_update("correct_power_off", True)
        mfl.flag_update("last_hour_downtime", time.strftime("%Y-%m-%d %H:%M:%S"))
        mfl.flag_update("last_uptime_count", _calculate_uptime())
        
        _cleanup_logs_if_needed()
        _handle_backups()
        
        stop_event.set()
        tsm.schedule_library_sanitizer()
        mfl.save_ram_flags()
        log.data_collection("ZORYA", "SHUTDOWN", "Shutting down Zorya...")
        time.sleep(10)
        
        global main_loop_continuity
        main_loop_continuity = False
    except Exception as e:
        log.data_collection("ZORYA", "ERROR", f"Error during shutdown sequence: {e}")
#________________________________________________________________________________________________________________________
#_________________________________________________EXECUTION DISPATCHER___________________________________________________
RESPONSE_EXCEPTION_FUNCTIONS = (
    "shut_down_sequence",
    "respond_self_features",
    "self_tell_joke",
    "self_save_new_vocab",
    "self_info_response_handler",
    "respond_self_query",
    "alert_flag_and_value_choice"
)

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
            rph.audio_text_synchronizer("ERROR")
            log.data_collection("ZORYA", "ERROR", f"Module not found: {action_module_name}")
            return
#--------------------------------------------------------------------------------------Find and execute the function
    try:
        action_function = getattr(target_module, action_function_name)
#--------------------------------------------------------------------------------------Exceptions to general execution
        if action_function_name in RESPONSE_EXCEPTION_FUNCTIONS :
            action_function(resolved_parameters)
        elif action_function_name == "set_talk_flag" and resolved_parameters == False:
            log.data_collection("ZORYA", "TALK", f"Executed {action_function_name}")
            rph.audio_text_synchronizer("SILENT")
            action_function(resolved_parameters)
        elif action_function_name == "set_talk_flag" and resolved_parameters == True:
            log.data_collection("ZORYA", "TALK", f"Executed {action_function_name}")
            action_function(resolved_parameters)
            rph.audio_text_synchronizer("TALK")
        elif action_module_name == "debug_module":
            rph.audio_text_synchronizer("DEBUG")
            action_function(resolved_parameters)
#---------------------------------------------------------------------------------------General execution
        elif action_function_name == "execute_command":
            rph.audio_text_synchronizer("EXECUTION")
            action_function(resolved_parameters)
            log.data_collection("ZORYA", "EXECUTE", f"Executed {action_function_name}.{resolved_parameters}")
        elif "INTENT_SYSTEM_OVERRIDE" in intent_id:
            rph.audio_text_synchronizer("DEBUG")
            action_function(resolved_parameters)
        
        else:
            rph.audio_text_synchronizer("EXECUTION")
            action_function(resolved_parameters)
            log.data_collection("ZORYA", "EXECUTE", f"Executed {action_module_name}.{action_function_name}.{resolved_parameters}") 
    except AttributeError:
        rph.audio_text_synchronizer("ERROR")
        log.data_collection("ZORYA", "ERROR", f"Function not found: {action_function_name} in {action_module_name}")
    except TypeError as e:
        rph.audio_text_synchronizer("ERROR")
        log.data_collection("ZORYA", "ERROR", f"Parameter mismatch: {action_function_name} - {e}")
    except Exception as e:
        rph.audio_text_synchronizer("ERROR")
        log.data_collection("ZORYA", "ERROR", f"Unexpected execution error: {e}")        
#________________________________________________________________________________________________________________________
#_____________________________________________________MAIN CLI LOOP______________________________________________________
if __name__ == "__main__":
    startup_sequence()
    log.data_collection("ZORYA", "CLI MODE", "CLI mode started.")
    while main_loop_continuity == True:
        try:
            usr_input = input("You: ")
            prm.self_user_tracking("increment")
            phrase_contract = interpreter.interpret_tokens(usr_input)
            if phrase_contract is not None:
                (intent_id, action_module_name, action_function_name, resolved_parameters) = phrase_contract
                execute_action(intent_id, action_module_name, action_function_name, resolved_parameters)
            else:
                rph.audio_text_synchronizer("ERROR")
                moem.self_alter_mood_failed_interpretation()
        except Exception as e:
            log.data_collection("ZORYA", "ERROR", f"Unexpected error in main loop: {e}")
#________________________________________________________________________________________________________________________
#________________________________________________________________________________________________________________________