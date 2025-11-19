import os
import json
from tkinter import Tk, filedialog
from . import log_handler as log
from . import interpretation_engine as interpreter

program_file_path = os.path.join(os.path.dirname(__file__), "Long_term_memory","program_path.json")
folder_file_path = os.path.join(os.path.dirname(__file__), "Long_term_memory", "folder_path.json")
batch_file_path = os.path.join(os.path.dirname(__file__), "Built_Batches")
program_paths = {}
folder_paths = {}

def load_program_paths():
    global program_paths
    try:
        with open(program_file_path, 'r', encoding='utf-8') as path_file:
            program_paths = json.load(path_file)
        return ("Program paths loaded", 0)
    except FileNotFoundError:
        log.data_collection("PROGRAM PATHS", "LOAD FILE", "Program paths file not found.")
        return ("Bad program paths file path", 1)
    except json.JSONDecodeError as e:
        log.data_collection("PROGRAM PATHS", "LOAD FILE", f"JSON parse error: {e}")
        return ("Malformed program paths file", 1)

def load_folder_paths():
    global folder_paths
    try:
        with open(folder_file_path, 'r', encoding='utf-8') as path_file:
            folder_paths = json.load(path_file)
        return ("Folder paths loaded", 0)
    except FileNotFoundError:
        log.data_collection("FOLDER PATHS", "LOAD FILE", "Folder paths file not found.")
        return ("Bad folder paths file path", 1)
    except json.JSONDecodeError as e:
        log.data_collection("FOLDER PATHS", "LOAD FILE", f"JSON parse error: {e}")
        return ("Malformed folder paths file", 1)
    
def get_executable_path_from_user():
    Tk().withdraw()
    path = filedialog.askopenfilename(
        title="Select executable file",
        filetypes=[("Executable Files", "*.exe"), ("All Files", "*.*")]
    )
    if path != "":
        return path

def get_folder_path_from_user():
    Tk().withdraw()
    path = filedialog.askdirectory(title="Select a folder")
    if path != "":
        return path

def get_program_path(program_name):
    return program_paths.get(program_name, None)

def set_program_path(dummy_parameter):
    global program_paths
    print("Tell me the name of the program you want to set the path for:")
    program_name = input("You: ")
    interpreter.save_new_vocabulary(f"OBJECT.APP.{program_name}")
    if program_name != "":
        from . import routine_builder_module as rbm
        rbm.self_build_routine(f"INTENT_OPEN_{program_name.upper()}",f"open the app {program_name}",["ACTION.OPEN",f"OBJECT.APP.{program_name}"],"system_control_module","call_program",program_name)
        path = get_executable_path_from_user()
        program_paths.update({program_name: path})
    try:
        with open(program_file_path, 'w', encoding='utf-8') as path_file:
            json.dump(program_paths, path_file, indent=4)
        log.data_collection("PROGRAM PATHS", "SET PATH", f"Set path for {program_name} to {path}")
    except Exception as e:
        log.data_collection("PROGRAM PATHS", "SET PATH ERROR", f"Error setting path for {program_name}: {e}")

def set_folder_path(dummy_parameter):
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
        log.data_collection("FOLDER PATHS", "SET PATH", f"Set path for {folder_name} to {path}")
    except Exception as e:
        log.data_collection("FOLDER PATHS", "SET PATH ERROR", f"Error setting path for {folder_name}: {e}")

def call_program(program_name):
    try:
        path = get_program_path(program_name)
        if path is None:
            raise ValueError
    except ValueError as e:
        log.data_collection("PROGRAM PATHS", "CALL PROGRAM ERROR", f"Error getting program path for {program_name}: {e}")
        print("I don't know that program yet. Can you show me the program's executable?")
        set_program_path("dummy_parameter")
        path = get_program_path(program_name)
        
    if path:
        try:
            os.startfile(path)  # Windows-specific
            log.data_collection("PROGRAM PATHS", "CALL PROGRAM", f"Called program {program_name} at {path}")
        except Exception as e:
            log.data_collection("PROGRAM PATHS", "CALL PROGRAM ERROR", f"Error calling program {program_name}: {e}")
    else:
        log.data_collection("PROGRAM PATHS", "CALL PROGRAM ERROR", f"Program path for {program_name} not found.")

def call_batch_script(dummy_parameter):
    script_name = input("Enter the name of the batch script (without extension): ")
    script_name = script_name + ".bat"
    batch_file = os.path.join(batch_file_path, script_name)
    try:
        os.startfile(batch_file)  # Windows-specific
        log.data_collection("PROGRAM PATHS", "CALL BATCH SCRIPT", f"Called batch script at {script_name}")
        print(f"Batch script {script_name} sucessfull")
    except Exception as e:
        log.data_collection("PROGRAM PATHS", "CALL BATCH SCRIPT ERROR", f"Error calling batch script: {e}")                                                                              

def open_specific_directory(directory_name):
    try:
        path = folder_paths.get(directory_name, None)
        if path:
            os.startfile(path)  # Windows-specific
            log.data_collection("FOLDER PATHS", "OPEN DIRECTORY", f"Opened directory {directory_name} at {path}")
        else:
            log.data_collection("FOLDER PATHS", "OPEN DIRECTORY ERROR", f"Directory path for {directory_name} not found.")
    except Exception as e:
        log.data_collection("FOLDER PATHS", "OPEN DIRECTORY ERROR", f"Error opening directory {directory_name}: {e}")
        
def force_close_program(dummy_parameter):
    usr_input = input("What program do you want to close? ")
    os.system(f"taskkill /f /im {usr_input}.exe")