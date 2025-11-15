import subprocess
from . import log_handler as log

def _run_system_command(command):
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            check=True
        )
        if result.stdout:
            print("\n--- Command Output ---")
            print(result.stdout.strip())
            print("----------------------\n")
            
        log.data_collection("COMMAND RUNNER", "RUN COMMAND", f"Executed command: {command}. Return Code: {result.returncode}")
        
    except subprocess.CalledProcessError as e:
        error_message = f"Command failed with return code {e.returncode}:\n{e.stderr.strip()}"
        print(f"\n--- Command Error ---\n{error_message}\n---------------------\n")
        log.data_collection("COMMAND RUNNER", "RUN COMMAND ERROR", error_message)
    except Exception as e:
        error_message = f"Error executing command '{command}': {e}"
        print(f"\n--- Execution Error ---\n{error_message}\n-----------------------\n")
        log.data_collection("COMMAND RUNNER", "RUN COMMAND ERROR", error_message)

def load_cmd(dummy_parameter):
    running_flag = True
    log.data_collection("COMMAND RUNNER", "START", "Command runner started.")
    print("To exit command runner, type 'exit_cmd'.")
    while running_flag:
        user_input = input("Enter system command: ")
        if user_input.strip().lower() == "exit_cmd":
            running_flag = False
            print("Exiting command runner.")
            log.data_collection("COMMAND RUNNER", "EXIT", "Command runner exited by user.")
        else:
            _run_system_command(user_input)
        