import os
import sys
import time
import psutil
import Data.memory_flags_loader as mfl
import Data.interpretation_engine as interpreter
import Data.system_control_module as scm
import Data.log_handler as log
import Data.routine_builder_module as rbm
import Data.system_watcher_module as swm
import Data.response_handler as rph
import Data.task_scheduler_module as tsm


def memory_usage():
    process = psutil.Process(os.getpid())
    mem_bytes = process.memory_info().rss
    mem_kb = mem_bytes / 1024
    return(f"Memory usage: {mem_kb:.2f} KB")

def load_assets():
    startup_errors = 0
    mfl.flag_update("startup_errors", startup_errors)

    def error_handler(module_flag, module_type, is_critical):
        nonlocal error_catch, essential_modules_error
        error_flags.append(module_flag[0])
        print(f"Error loading {module_type}: {module_flag[0]}")
        error_catch += 1
        if is_critical:
            essential_modules_error += 1
    
    error_catch = 0
    essential_modules_error = 0
    error_flags = []
    print("Starting up Zorya...")
#----------------------------------------------------------------memory flags load
    mfl_flag = mfl.memory_load()
    if mfl_flag[1] != 0:
        error_handler(mfl_flag, "memory flags",True)
    else:
        print("Memory flags loaded...")
#----------------------------------------------------------------response library load
    rph_flag = rph.load_response_library()
    if rph_flag[1] != 0:
        error_handler(rph_flag, "response library",True)
    else:
        print("Response library loaded...")
#----------------------------------------------------------------vocabulary load
    vocabulary_flag = interpreter.vocabulary_load()
    if vocabulary_flag[1] != 0:
        error_handler(vocabulary_flag, "vocabulary", True)
    else:
        print("Vocabulary loaded...")
#----------------------------------------------------------------intent map load
    intent_map_flag = interpreter.intent_map_load()
    if intent_map_flag[1] != 0:
        error_handler(intent_map_flag, "intent map", True)
    else:
        print("Intent map loaded...")
#----------------------------------------------------------------program paths load
    program_path_flag = scm.load_program_paths()
    if program_path_flag[1] != 0:
        error_handler(program_path_flag, "program paths", False)
    else:
        print("Program paths loaded...")
#----------------------------------------------------------------folder paths load
    folder_path_flag = scm.load_folder_paths()
    if folder_path_flag[1] != 0:
        error_handler(folder_path_flag, "folder paths", False)
    else:
        print("Folder paths loaded...")
#----------------------------------------------------------------routine buffer load
    routine_buffer_flag = rbm.load_short_memory()
    if routine_buffer_flag[1] != 0:
        error_handler(routine_buffer_flag, "short term memory file", False)
    else:
        print("Short memory loaded...")
#----------------------------------------------------------------schedule loader
    schedule_flag = tsm.load_schedule_library()
    if schedule_flag[1] != 0:
        error_handler(schedule_flag, "schedule library", False)
    else:
        print("Schedule library loaded...")
#----------------------------------------------------------------apps blacklist load
    wgb_flag = swm.load_wgb_list()
    if wgb_flag[1] != 0:
        error_handler(wgb_flag, "apps blacklist", False)
    else:
        print("Apps blacklist loaded...")
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
#-----------------------------------------------------------------stale paths verification step
    stale_paths_result = scm.self_remove_deleted_programs_from_mem()
    if stale_paths_result[1] != 0:
        error_handler(stale_paths_result, "stale paths verification", False)
    else:
        print(stale_paths_result[0])
#-----------------------------------------------------------------stale mem entry verification step
    known_programs = scm.all_known_programs()
    sanitized_entries = mfl.sanitize_memory_programs(known_programs)
    if sanitized_entries[1] != 0:
        error_handler(sanitized_entries, "stale memory entries verification", False)
    else:
        print(sanitized_entries[0])
#-----------------------------------------------------------------stale intent verification step
    known_programs = scm.all_known_programs()
    sanitized_intents = interpreter.sanitize_stale_program_intents(known_programs)
    if sanitized_intents[1] != 0:
        error_handler(sanitized_intents, "stale intents verification", False)
    else:
        print(sanitized_intents[0])
#-----------------------------------------------------------------final report
    if error_catch != 0 and essential_modules_error == 0:
        startup_errors += error_catch
        print("Errors occurred during startup, runtime might be unstable. Refer to logs for details.")
        log.data_collection("BOOTSRAPPER", "ERROR", f"Startup completed with {error_catch} errors.")
        mfl.flag_update("startup_errors", startup_errors)
        for error in error_flags:
            log.data_collection("BOOTSRAPPER", "ERROR", f"Startup error: {error}")
    elif essential_modules_error != 0:
        print("\033[91mCatastrophic errors occurred during startup. Refer to logs for details.\033[0m")
        log.data_collection("BOOTSRAPPER", "ERROR", f"Startup completed with {essential_modules_error} critical errors.")
        time.sleep(5)
        sys.exit(1)
    else:
        print("All assets loaded successfully.")
        log.data_collection("BOOTSRAPPER", "STARTUP", "Basic operation health check and startup completed successfully.")
        rph.audio_text_synchronizer("START_UP")
        time.sleep(5)
    usr_input = input("Press Enter to continue...")