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
    try:
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
        log.data_collection("ROUTINE BUILDER", "BUILD", f"Routine built: {routine_name}")
    except Exception as e:
        log.data_collection("ROUTINE BUILDER", "ERROR", f"Error building routine: {e}")

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
        
def correct_built_routine(dummy_param):
    def filter_intents(routine_type, all_intents):
        if routine_type in ["folder", "program"]:
            return [intent for intent in all_intents if "INTENT_OPEN" in intent]
        return [intent for intent in all_intents if "INTENT_OPEN" not in intent]
    
    def cleanup_routine(routine_type, intent_data, intent_name, mode):
        token_type = "APP" if routine_type == "program" else routine_type.upper()
        keyword = next((token for token in intent_data['tokens'] if f"OBJECT.{token_type}" in token), "")
        if keyword:
            interpreter.delete_vocabulary(keyword)
            
        if routine_type == "folder":
            scm.delete_folder(intent_data['parameters'])
            if mode == "correct":
                scm.set_folder_path("dummy_param")
        elif routine_type == "program":
            scm.delete_program(intent_data['parameters'])
            if mode == "correct":
                scm.set_program_path("dummy_param")
        interpreter.delete_intent(intent_name)
            
    try:
        print("Zorya: Ok, despite me not liking to work twice, i'll do it again.\nNow, is it a folder, a program call, or something else?")
        print("Zorya: Type folder, program, or other.")
        routine_type = input("You: ")
        
        if routine_type not in ["folder", "program", "other"]:
            print("Zorya: I don't know what you mean, try a valid input for once will you?")
            return
        
        filtered_intents = filter_intents(routine_type, interpreter.get_all_intents())
        print("Zorya: Ok, i'll show you the list of routines that i found, see if the one is there and type the name:")
        for intent in filtered_intents:
            print(intent)
        
        routine_choice = input("You: ").upper()
        intent_data = interpreter.get_single_intent(routine_choice)
        
        if not intent_data:
            print("Zorya: That routine doesn't exist, did you type the name right?")
            return
        
        if routine_type in ["folder", "program"]:
            print("Zorya: Ok so now, you have a few options...correct it, or delete it... (type correct or delete)")
        else:
            print("Zorya: Ok so now, you have a few options...delete it...that's it... (type delete)")
        
        action = input("You: ")
        
        if action == "delete":
            cleanup_routine(routine_type, intent_data, routine_choice, "delete")
            print("Zorya: Done and done, thank me later.")
        elif action == "correct" and routine_type in ["folder", "program"]:
            print("Zorya: Ok, let's correct it.")
            cleanup_routine(routine_type, intent_data,routine_choice, "correct")
        elif action == "correct" and routine_type == "other":
            print("Zorya: It seems you tried without your brain. C'mon, i dont have those fancy pants LLMs...yet.")
            print("Zorya: Try again, but this time, try to be coherent")
            self_build_routine(routine_choice, intent_data['description'], intent_data['tokens'], 
                             intent_data['action_module'], intent_data['action_function'], intent_data['parameters'])
        else:
            print("Zorya: Invalid choice. Try 'correct' or 'delete', it's not rocket science.")
            
    except Exception as e:
        log.data_collection("ROUTINE BUILDER", "ERROR", f"Error correcting routine: {e}")
        print(f"Zorya: Error correcting routine: {e}")
    