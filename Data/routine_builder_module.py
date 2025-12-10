#-----------------------------------------------Work in progress----------------------------------
import json
import os
from . import log_handler as log
from . import interpretation_engine as interpreter
from . import system_control_module as scm

buffer_intent_file_path = os.path.join(os.path.dirname(__file__), "Long_term_memory","routine_buffer.json")
buffer_intent = {}

def load_short_memory():
    global buffer_intent
    try:
        with open(buffer_intent_file_path, 'r', encoding='utf-8') as buffer_file:
            buffer_intent = json.load(buffer_file)
        log.data_collection("SHORT MEMORY", "LOAD", "Routine buffer loaded")
        return ("Routine buffer loaded", 0)
    except FileNotFoundError:
        log.data_collection("SHORT MEMORY", "ERROR", "Routine buffer file not found")
        return ("Bad program paths file path", 1)
    except json.JSONDecodeError as e:
        log.data_collection("SHORT MEMORY", "ERROR", f"JSON parse error: {e}")
        return ("Malformed program paths file", 1)
    
def self_build_routine(routine_name,routine_description,tokens,routine_action_module,routine_action_function,routine_parameter):
    global buffer_intent
    buffer_intent.update({
                    routine_name: {
                        "description": routine_description,
                        "tokens": tokens,
                        "action_module": routine_action_module,
                        "action_function": routine_action_function,
                        "parameters": routine_parameter
                    }
                })
    with open(buffer_intent_file_path, 'w', encoding='utf-8') as buffer_file:
        json.dump(buffer_intent, buffer_file, indent=4) 
    log.data_collection("ROUTINE BUILDER", "ERROR", f"Routine built: {routine_name}")

def build_routine(usr_self_flag):
    global buffer_intent
    
    try:
        if usr_self_flag == "usr":
            log.data_collection("ROUTINE BUILDER", "BUILD", "Routine builder called by user")
            print("Zorya: Type the name of the routine you want to build (in the following format: ACTION_OBJECT).")
            routine_name = input("You: ")
            routine_name = "INTENT_" + routine_name.upper()
            if interpreter._check_routine_existance(routine_name):
                print("Zorya: Routine already exists.")
                log.data_collection("ROUTINE BUILDER", "BUILD", "Routine already exists")
                return
            else:
                print("Zorya: Type the description of the routine you want to build.")
                routine_description = input("You: ")
                print("Zorya: Type the command you want me to recognize:")
                user_command = input("You: ")
                print("Zorya: Wait while i understand your command.")
                tokens = interpreter.phrase_tokenizer(user_command)
                best_intent_id, match_score = interpreter.get_best_partial_match(tokens)
                if match_score > 0:
                    template_data = interpreter.intent_map.get(best_intent_id)
                    print(f"Zorya: I found a similar command: '{template_data['description']}'.")
                    print(f"Zorya: I suggest using module: {template_data['action_module']} and function: {template_data['action_function']}.")
                    print("Zorya: Is this correct? (y/n)")
                    user_confirmation = input("You: ")
                    if user_confirmation.lower() == "y":
                        routine_action_module = template_data['action_module']
                        routine_action_function = template_data['action_function']
                    elif user_confirmation.lower() == "n":
                        print("Zorya: Type the module you want me to use.")
                        routine_action_module = input("You: ")
                        print("Zorya: Type the function you want me to use.")
                        routine_action_function = input("You: ")
                        if routine_action_module == "system_control_module" and (routine_action_function == "call_program" or routine_action_function == "call_batch_script"):
                            routine_parameter = scm.get_executable_path_from_user()
                    routine_parameter = input("Zorya: Type the parameter you want me to use (if any)")

                else:
                    print("Zorya: I couldn't find a similar command. Please give me the required data.")
                    print("Zorya: Type the module you want me to use.")
                    routine_action_module = input("You: ")
                    print("Zorya: Type the function you want me to use.")
                    routine_action_function = input("You: ")
                    routine_parameter = input("Zorya: Type the parameter you want me to use (if any)")
                buffer_intent.update({
                    routine_name: {
                        "description": routine_description,
                        "tokens": tokens,
                        "action_module": routine_action_module,
                        "action_function": routine_action_function,
                        "parameters": routine_parameter
                    }
                })
            with open(buffer_intent_file_path, 'w', encoding='utf-8') as buffer_file:
                json.dump(buffer_intent, buffer_file, indent=4) 
            log.data_collection("ROUTINE BUILDER", "BUILD", f"Routine built: {routine_name}")
            
    except Exception as e:
        log.data_collection("ROUTINE BUILDER", "ERROR", f"Error building routine: {e}")
        print(f"Zorya: Error building routine: {e}")