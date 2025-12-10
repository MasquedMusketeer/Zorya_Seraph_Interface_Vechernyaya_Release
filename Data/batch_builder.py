import os
from . import log_handler as log

_batch_folder = os.path.join(os.path.dirname(__file__), "Built_Batches")
_batch_command_list = []

def _register_batch_command(command):
    global _batch_command_list
    _batch_command_list.append(command)

def _save_batch_commands(batch_name):
    global _batch_command_list
    global _batch_folder
    if not os.path.exists(_batch_folder):
        os.makedirs(_batch_folder)
    batch_file_path = os.path.join(_batch_folder, f"{batch_name}.bat")
    with open(batch_file_path, 'w', encoding='utf-8') as batch_file:
        for command in _batch_command_list:
            batch_file.write(f"{command}\n")

def batch_orchestrator(dummy_parameter):
    global _batch_command_list
    orchestrator_operation = True
    try:
        while orchestrator_operation:
            print("Zorya: Type bellow one line of the batch file you want to create,")
            print(" then press Enter to continue. When you are done, type 'SAVE BATCH'.")
            user_input = input("You: ")
            if user_input.upper() == "SAVE BATCH":
                batch_name = input("Zorya: Enter the name for the batch file (without extension, use _ for spaces in the name)\nYou: ")
                _save_batch_commands(batch_name)
                print(f"Zorya: Batch file '{batch_name}.bat' saved successfully.")
                log.data_collection("BATCH", "SAVE", f"Batch file '{batch_name}.bat' created with {_batch_command_list.__len__()} commands.")
                orchestrator_operation = False
                _batch_command_list.clear()
            else:
                _register_batch_command(user_input)
    except Exception as e:
        log.data_collection("BATCH", "ERROR", f"Error creating batch file: {e}")
            