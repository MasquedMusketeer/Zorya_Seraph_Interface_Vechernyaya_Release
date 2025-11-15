import os
import json
from . import log_handler as log

program_file_path = os.path.join(os.path.dirname(__file__), "Long_term_memory","program_path.json")
batch_file_path = os.path.join(os.path.dirname(__file__), "Built_Batches")
program_paths = {}

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

def get_program_path(program_name):
    return program_paths.get(program_name, None)

def set_program_path(program_name, path):
    program_paths[program_name] = path
    try:
        with open(program_file_path, 'w', encoding='utf-8') as path_file:
            json.dump(program_paths, path_file, indent=4)
        log.data_collection("PROGRAM PATHS", "SET PATH", f"Set path for {program_name} to {path}")
    except Exception as e:
        log.data_collection("PROGRAM PATHS", "SET PATH ERROR", f"Error setting path for {program_name}: {e}")

def call_program(program_name):
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