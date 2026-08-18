import os
import subprocess
import json
import time
from tkinter import Tk, filedialog
from . import log_handler as log
from . import interpretation_engine as interpreter
from . import mood_engine_module as moem

program_file_path = os.path.join(os.path.dirname(__file__), "Long_term_memory","program_path.json")
temp_program_file_path = os.path.join(os.path.dirname(__file__), "Long_term_memory", "program_path_temp.json")
folder_file_path = os.path.join(os.path.dirname(__file__), "Long_term_memory", "folder_path.json")
batch_file_path = os.path.join(os.path.dirname(__file__), "Built_Batches")
program_paths = {}
temp_program_paths = {}
folder_paths = {}
program_launcher_queue = []

#_________________________________________________________________________________________________________________________
#____________________________________________________ASSETS HANDLER_______________________________________________________
def load_program_paths():
    global program_paths
    global temp_program_paths
    try:
        with open(program_file_path, 'r', encoding='utf-8') as path_file:
            program_paths = json.load(path_file)
        with open(temp_program_file_path, 'r', encoding='utf-8') as temp_path_file:
            temp_program_paths = json.load(temp_path_file)
        return ("Program paths loaded", 0)
    except FileNotFoundError:
        log.data_collection("PROGRAM PATHS", "ERROR", "Program paths file not found.")
        return ("Bad program paths file path", 1)
    except json.JSONDecodeError as e:
        log.data_collection("PROGRAM PATHS", "ERROR", f"JSON parse error: {e}")
        return ("Malformed program paths file", 1)

def load_folder_paths():
    global folder_paths
    try:
        with open(folder_file_path, 'r', encoding='utf-8') as path_file:
            folder_paths = json.load(path_file)
        return ("Folder paths loaded", 0)
    except FileNotFoundError:
        log.data_collection("FOLDER PATHS", "ERROR", "Folder paths file not found.")
        return ("Bad folder paths file path", 1)
    except json.JSONDecodeError as e:
        log.data_collection("FOLDER PATHS", "ERROR", f"JSON parse error: {e}")
        return ("Malformed folder paths file", 1)
#_________________________________________________________________________________________________________________________
#_______________________________________________STARTUP APPS HANDLER______________________________________________________
def startup_apps_on_power_on(startup_apps, visible_apps):
    try:
        for s_app in startup_apps:
            app_is_running = any(s_app.lower() in r.lower() for r in visible_apps)
            if not app_is_running:
                call_program(s_app)
                log.data_collection("SCM", "STARTUP APP", f"Added {s_app} on run queue.")
            else:
                log.data_collection("SCM", "STARTUP APP", f"{s_app} is already running.")
    except Exception as e:
        log.data_collection("SCM", "ERROR", f"Error starting up apps: {e}")

def set_new_startup_app(_):
    try:
        import Data.memory_flags_loader as mfl
        global program_paths
        startup_apps = mfl.flag_return("apps_expected_at_start")
        app_name = input("Enter the name of the program you want to run at startup: ")
        app_name = app_name.lower()
        if app_name not in program_paths:
            log.data_collection("ZORYA", "SET STARTUP APP", f"No program found, setting new program path for {app_name}")
            print(f"Program {app_name} not found.")
            print("Initializing new program registration.")
            set_program_path(None)
        startup_apps.append(app_name)
        mfl.flag_update("apps_expected_at_start", startup_apps)
        mfl.save_ram_flags()
        log.data_collection("SCM", "SET STARTUP APP", f"New startup program set: {app_name}")
        moem.self_alter_mood_feeling_useful()
    except Exception as e:
        log.data_collection("SCM", "ERROR", f"Error setting new startup program: {app_name}: {e}")

def remove_startup_app(_):
    try:
        import Data.memory_flags_loader as mfl
        startup_apps = mfl.flag_return("apps_expected_at_start")
        presentable_string = ""
        for app in startup_apps:
            presentable_string += app + ", "
        print(f"Zorya: Enter the name of the program you want to remove from startup. current ones: {presentable_string}.")
        app_name = input("You: ")
        app_name = app_name.lower()
        if app_name in startup_apps:
            startup_apps.remove(app_name)
            mfl.flag_update("apps_expected_at_start", startup_apps)
            log.data_collection("SCM", "DELETE STARTUP APP", f"Removed program {app_name} from startup initialization.")
        elif app_name == "no" or app_name == "none":
            print("Zorya: Alright, no problem.")
            log.data_collection("SCM", "DELETE STARTUP APP", "No program removed from startup initialization by user choice.")
        else:
            log.data_collection("SCM", "DELETE STARTUP APP", f"Program {app_name} not found.")
            print("Zorya: Are you sure you typed that right? Try again, but this time, pay attention...please...")
    except Exception as e:
        log.data_collection("SCM", "ERROR", f"Error removing program {app_name} from startup: {e}")
#_________________________________________________________________________________________________________________________
#___________________________________________________PROGRAM HANDLER_______________________________________________________    
def get_executable_path_from_user():
    Tk().withdraw()
    path = filedialog.askopenfilename(
        title="Select executable file",
        filetypes=[("Executable Files", "*.exe"), ("All Files", "*.*")]
    )
    if path != "":
        return path

def get_program_path(program_name):
    return program_paths.get(program_name, None)

def set_program_path(_):
    try:
        from . import memory_flags_loader as mfl
        global program_paths
        print("Zorya: Tell me the name of the program you want to set the path for.")
        program_name = input("You: ")
        interpreter._save_vocabulary(f"OBJECT.APP.{program_name}")
        if program_name != "":
            from . import routine_builder_module as rbm
            rbm.self_build_routine(f"INTENT_OPEN_{program_name.upper()}",f"open the app {program_name}",["ACTION.OPEN",f"OBJECT.APP.{program_name}"],"system_control_module","call_program",program_name)
            path = get_executable_path_from_user()
            program_paths.update({program_name: path})
            silenced_apps = mfl.flag_return("silenced_apps")
            silenced_apps.update({program_name: "silence"})
            mfl.flag_update("silenced_apps", silenced_apps)
        else:
            print("Zorya: You didn't provide a valid program name.")
            return

        with open(program_file_path, 'w', encoding='utf-8') as path_file:
            json.dump(program_paths, path_file, indent=4)
        log.data_collection("SCM", "SET PATH", f"Set path for {program_name} to {path}")
        moem.self_alter_mood_feeling_useful()
    except Exception as e:
            log.data_collection("SCM", "ERROR", f"Error setting path for {program_name}: {e}")

def delete_program_path(program_name):
    global program_paths
    global temp_program_paths
    if program_name in program_paths:
        try:
            del program_paths[program_name]
            with open(program_file_path, 'w', encoding='utf-8') as path_file:
                json.dump(program_paths, path_file, indent=4)
            log.data_collection("SCM", "DELETE PATH", f"Deleted path for {program_name}")
        except Exception as e:
            log.data_collection("SCM", "ERROR", f"Error deleting path for {program_name}: {e}")
    elif program_name in temp_program_paths:
        try:
            del temp_program_paths[program_name]
            with open(temp_program_file_path, 'w', encoding='utf-8') as path_file:
                json.dump(temp_program_paths, path_file, indent=4)
            log.data_collection("SCM", "DELETE PATH", f"Deleted path for {program_name}")
        except Exception as e:
            log.data_collection("SCM", "ERROR", f"Error deleting path for {program_name}: {e}")
    #_________________________________________________________________________________________________________________________
#____________________________________________________FOLDER HANDLER_______________________________________________________ 
def get_folder_path_from_user():
    Tk().withdraw()
    path = filedialog.askdirectory(title="Select a folder")
    if path != "":
        return path

def set_folder_path(_):
    global folder_paths
    folder_name = input("Enter the name of the folder: ")
    interpreter.save_new_vocabulary(f"OBJECT.FOLDER.{folder_name}")
    if folder_name != "":
        from . import routine_builder_module as rbm
        rbm.self_build_routine(f"INTENT_OPEN_{folder_name.upper()}",f"open the app {folder_name}",["ACTION.OPEN",f"OBJECT.FOLDER.{folder_name}"],"system_control_module","open_specific_directory",folder_name)
        path = get_folder_path_from_user()
        folder_paths.update({folder_name: path})
    
    try:
        with open(folder_file_path, 'w', encoding='utf-8') as path_file:
            json.dump(folder_paths, path_file, indent=4)
        log.data_collection("SCM", "SET PATH", f"Set path for {folder_name} to {path}")
        moem.self_alter_mood_feeling_useful()
    except Exception as e:
        log.data_collection("SCM", "ERROR", f"Error setting path for {folder_name}: {e}")

def delete_folder_path(folder_name):
    global folder_paths
    try:
        del folder_paths[folder_name]
        with open(folder_file_path, 'w', encoding='utf-8') as path_file:
            json.dump(folder_paths, path_file, indent=4)
        log.data_collection("SCM", "DELETE PATH", f"Deleted path for {folder_name}")
    except Exception as e:
        log.data_collection("SCM", "ERROR", f"Error deleting path for {folder_name}: {e}")
#_________________________________________________________________________________________________________________________
#_________________________________________________EXECUTION HANDLER_______________________________________________________ 
def call_program(program_name):
    global program_launcher_queue
    try:
        path = get_program_path(program_name)
        if path is None:
            raise ValueError
        else:
            program_launcher_queue.append(program_name)
    except ValueError as e:
        log.data_collection("PROGRAM PATHS", "ERROR", f"Error getting program path for {program_name}: {e}")
        print("Zorya: I don't know that program yet. Can you show me the program's executable?")
        set_program_path("dummy_parameter")
        path = get_program_path(program_name)
        if path is not None:
            program_launcher_queue.append(program_name)
        else:
            log.data_collection("SCM", "ERROR", f"Error calling program {program_name}: Path not found")
            return

def run_program_from_queue(stop_event):
    while not stop_event.is_set():
        global program_launcher_queue
        if program_launcher_queue:
            program_name = program_launcher_queue.pop(0)
            path = get_program_path(program_name)
            if path:
                try:
                    os.startfile(path)  # Windows-specific
                    log.data_collection("SCM", "RUN PROGRAM", f"Called program {program_name} at {path}")
                    moem.self_alter_mood_feeling_useful()
                except Exception as e:
                    log.data_collection("SCM", "ERROR", f"Error calling program {program_name}: {e}")
            else:
                log.data_collection("SCM", "ERROR", f"Program path for {program_name} not found.")
        time.sleep(5)

def call_batch_script(_):
    script_name = input("Enter the name of the batch script (without extension): ")
    script_name = script_name + ".bat"
    batch_file = os.path.join(batch_file_path, script_name)
    try:
        os.startfile(batch_file)  # Windows-specific
        log.data_collection("SCM", "CALL BATCH SCRIPT", f"Called batch script at {script_name}")
        print(f"Batch script {script_name} sucessfull")
        moem.self_alter_mood_feeling_useful()
    except Exception as e:
        log.data_collection("SCM", "ERROR", f"Error calling batch script: {e}")                                                                              

def open_specific_directory(directory_name):
    try:
        path = folder_paths.get(directory_name, None)
        if path:
            os.startfile(path)  # Windows-specific
            log.data_collection("SCM", "OPEN DIRECTORY", f"Opened directory {directory_name} at {path}")
        else:
            log.data_collection("SCM", "ERROR", f"Directory path for {directory_name} not found.")
        moem.self_alter_mood_feeling_useful()
    except Exception as e:
        log.data_collection("SCM", "ERROR", f"Error opening directory {directory_name}: {e}")
        
def force_close_program(_):
    print("Zorya: Which program do you want me to anihilate??")
    usr_input = input("You: ")
    try:
        subprocess.run(["taskkill", "/f", "/im", f"{usr_input}.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        log.data_collection("SCM", "FORCE KILL PROGRAM", f"Force killed program by user: {usr_input}")
        moem.self_alter_mood_feeling_useful()
    except Exception as e:
        log.data_collection("SCM", "ERROR", f"Error force killing program by user{usr_input}: {e}")

def self_kill_program(app):
    try:
        subprocess.run(["taskkill", "/f", "/im", f"{app}.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        log.data_collection("SCM", "FORCE KILL PROGRAM", f"Force killed program: {app}")
        moem.self_alter_mood_feeling_useful()
    except Exception as e:
        log.data_collection("SCM", "ERROR", f"Error force killing program {app}: {e}")

#_________________________________________________________________________________________________________________________
#_______________________________________________NEW PROGRAMS HANDLER______________________________________________________  
#                             Used to gather and save new paths from frequent executables.
def return_programs_not_known():
    try:
        from . import memory_flags_loader as mfl
        unknown_programs_not_ignored = []
        known_programs = all_known_programs()
        recent_programs = list(mfl.flag_return("apps_recently_used").keys())
        for program in known_programs:
            if program in recent_programs:
                recent_programs.remove(program)
        unknown_programs = recent_programs.copy()
        recent_programs = mfl.flag_return("apps_recently_used").copy()
        for program in unknown_programs:
            if isinstance(recent_programs[program], int):
                unknown_programs_not_ignored.append(program)
        return unknown_programs_not_ignored 
    except Exception as e:
        log.data_collection("SCM", "ERROR", f"Error getting unknown programs: {e}")

def all_known_programs():
    global program_paths
    global temp_program_paths
    known_programs = []
    for program_name, path in program_paths.items():
        known_programs.append(program_name)
    for program_name, path in temp_program_paths.items():
        known_programs.append(program_name)
    return known_programs
    
def self_set_program_path(name,path):
    temp_program_paths.update({name: path})
    try:
        with open(temp_program_file_path, 'w', encoding='utf-8') as path_file:
            json.dump(temp_program_paths, path_file, indent=4)
        log.data_collection("SCM", "SET PATH", f"Set path for {name} to {path}")
    except Exception as e:
        log.data_collection("SCM", "ERROR", f"Error setting path for {name}: {e}")
        
def self_temp_to_disk(app):
    global program_paths
    global temp_program_paths
    try:
        if app in temp_program_paths:
            program_paths.update({app: temp_program_paths[app]})
            del temp_program_paths[app]
            with open(program_file_path, 'w', encoding='utf-8') as path_file:
                json.dump(program_paths, path_file, indent=4)
            with open(temp_program_file_path, 'w', encoding='utf-8') as path_file:
                json.dump(temp_program_paths, path_file, indent=4)
            log.data_collection("SCM", "SET PATH", f"Moved {app} from temp to disk")
    except Exception as e:
            log.data_collection("SCM", "ERROR", f"App {app} not found in temp")
            
def self_ignore_temp(app):
    global temp_program_paths
    try:
        if app in temp_program_paths:
            del temp_program_paths[app]
            with open(temp_program_file_path, 'w', encoding='utf-8') as path_file:
                json.dump(temp_program_paths, path_file, indent=4)
            log.data_collection("SCM", "SET PATH", f"Ignored {app} in temp")
    except Exception as e:
            log.data_collection("SCM", "ERROR", f"App {app} not found in temp")  
#_________________________________________________________________________________________________________________________
#____________________________________________STALE PROGRAM PATHS HANDLER__________________________________________________ 
def self_remove_deleted_programs_from_mem():
    global program_paths
    global temp_program_paths
    try:
        known_programs = all_known_programs()
        known_parths = {**program_paths, **temp_program_paths}
        stale_paths = []
        for program in known_programs:
            verification_result_program_paths = os.path.exists(known_parths[program])
            if verification_result_program_paths == False:
                stale_paths.append(program)
        for program in stale_paths:
            delete_program_path(program)
        if stale_paths == []:
            log.data_collection("SCM", "REMOVE STALE PATHS", "No stale paths found")
            return ("No stale paths to remove",0)
        else:
            log.data_collection("SCM", "REMOVE STALE PATHS", f"Removed stale paths: {stale_paths}")
            moem.self_alter_mood_feeling_useful()
            return (f"Stale paths removed: {stale_paths}", 0)
    except Exception as e:
        log.data_collection("SCM", "ERROR", f"Error removing stale programs: {e}")
        return (f"Error removing stale programs: {e}", 1)
    

