import importlib
from . import log_handler as log

def arbitrary_function_execution(dummy_parameter):
    print("#------THIS IS A DEV FEATURE, IF YOU ARE HERE, YOU HAVE TO KNOW WHAT YOU ARE DOING------#")
    print("Zorya: To exit the execution loop, type 'exit' in any of the 3 prompts...")
    loop_tracker = True
    while loop_tracker:
        print("Zorya: Enter the module, function, and parameter (if any) to execute: ")
        usr_get_module = input("Module name: ")
        usr_get_function = input("Function name: ")
        usr_get_param = input("Parameter: ")
        if usr_get_function == "exit" or usr_get_module == "exit" or usr_get_param == "exit":
            loop_tracker = False
            break
        else:
            try:
                module = importlib.import_module(usr_get_module)
                function = getattr(module, usr_get_function)
                if usr_get_param == "":
                    function()
                else:
                    function(usr_get_param)
                log.data_collection("ARBITRARY FUNCTION EXECUTION", "EXECUTED", f"Executed {usr_get_function} from {usr_get_module} with parameter {usr_get_param}")
                print("Zorya: Function executed successfully, cheers!!")
            except Exception as e:
                log.data_collection("ARBITRARY FUNCTION EXECUTION", "ERROR", f"Error executing {usr_get_function} from {usr_get_module}: {e}")
                print(f"Zorya: I told you didn't i? it messed up me: {e}")