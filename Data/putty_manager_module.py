from . import log_handler as log
import os
import json
try:
    import paramiko as ssh
except ImportError:
    log.data_collection("SSH", "IMPORT ERROR", "Paramiko not installed, installing...")
    print("Zorya: I need to install paramiko, please wait...")
    from . import command_runner as cr
    cr._run_system_command("pip install paramiko")
    try:
        import paramiko as ssh
        log.data_collection("SSH", "IMPORT", "Paramiko installed successfully.")
    except ImportError:
        log.data_collection("SSH", "ERROR", "Paramiko installation failed.")
        print("Zorya: Paramiko installation failed, please try again.")
        raise

ssh_prof_file = os.path.join(os.path.dirname(__file__), "Long_term_memory", "ssh_profile_dict.json")
ssh_prof_dict = {}

def save_new_profile(profile_name, host, username, port):
    global ssh_prof_dict
    ssh_prof_dict[profile_name] = {"host": host, "username": username, "port": port}
    try:
        with open(ssh_prof_file, 'w', encoding='utf-8') as file:
            json.dump(ssh_prof_dict, file, indent=4)
        log.data_collection("SSH", "SAVE", f"New SSH profile '{profile_name}' saved successfully.")
    except Exception as e:
        log.data_collection("SSH", "ERROR", f"Error saving SSH profile '{profile_name}': {e}")

def load_ssh_profile_dict():
    global ssh_prof_dict
    try:
        with open(ssh_prof_file, 'r', encoding='utf-8') as file:
            ssh_prof_dict = json.load(file)
            log.data_collection("SSH", "LOAD", "SSH profile dictionary loaded successfully.")
            return ("ssh profiles loaded...", 0)
    except FileNotFoundError as e:
        log.data_collection("SSH", "ERROR", f"Error loading SSH profile dictionary, {e}.")
        return ("ssh profiles not found...", 1)
    except json.JSONDecodeError as e:
        log.data_collection("SSH", "ERROR", f"Error decoding SSH profile dictionary: {e}")
        return ("error loading ssh profiles...", 1)

def _ssh_connect(host, username, password,port):
    try:
        ssh_client = ssh.SSHClient()
        ssh_client.set_missing_host_key_policy(ssh.AutoAddPolicy())
        ssh_client.connect(host, username=username, password=password,port = port)
        log.data_collection("SSH", "CONNECT", f"Connected to {host} as {username}")
        return ssh_client
    except Exception as e:
        log.data_collection("SSH", "ERROR", f"Error connecting to {host}: {e}")
        print(f"Zorya: Error connecting to {host}: {e}")
        return None
def _ssh_disconnect(ssh_client):
    try:
        ssh_client.close()
        log.data_collection("SSH", "DISCONNECT", "Disconnected from SSH")
    except Exception as e:
        log.data_collection("SSH", "ERROR", f"Error disconnecting from SSH: {e}")
        print(f"Zorya: Error disconnecting from SSH: {e}")

def ssh_connection_orchestrator(dummy_param):
    print("Zorya: Do you want to load a previous profile? (y/n): ")
    usr_choice = input("You: ")
    if usr_choice.lower() == "y":
        print("--------------------------")
        print("   Available profiles:")
        print("--------------------------")
        for profile in ssh_prof_dict:
            print(profile)
        print("Zorya: Enter the name of the profile to load: ")
        usr_prof_choice = input("You: ")
        if usr_prof_choice in ssh_prof_dict:
            profile_data = ssh_prof_dict[usr_prof_choice]
            if "port" in profile_data:
                ssh_client = _ssh_connect(profile_data["host"], profile_data["username"], input("Enter the password: "), profile_data["port"])
            else:
                ssh_client = _ssh_connect(profile_data["host"], profile_data["username"], input("Enter the password: "), 22)
            if ssh_client:
                print("Zorya: Connected to SSH successfully.")
                log.data_collection("SSH", "CONNECT", f"Connected to {profile_data['host']} as {profile_data['username']}")
                while True:
                    command = input("Enter command (or 'exit' to disconnect): ")
                    if command.lower() == 'exit':
                        _ssh_disconnect(ssh_client)
                        break
                    stdin, stdout, stderr = ssh_client.exec_command(command)
                    output = stdout.read().decode('utf-8')
                    error = stderr.read().decode('utf-8')
                    if output:
                        print(f"Output:\n{output}")
                    if error:
                        print(f"Error:\n{error}")
    elif usr_choice.lower() == "n":
        print("Zorya: Ok, but i need the information to connect, you don't expect me to just guess right?")
        input_host = input("Enter the host to connect to: ")
        input_port = input("Enter the port to connect to: ")
        input_username = input("Enter the username: ")
        input_password = input("Enter the password: ")
        ssh_client = _ssh_connect(input_host, input_username, input_password, input_port)
        if ssh_client:
            print("Zorya: Connected to SSH successfully.")
            print("Zorya: Do you want to save this profile? (y/n):")
            usr_save_prof_choice = input("You: ")
            if usr_save_prof_choice.lower() == "y":
                print("Zorya: Ok, what do you want to call the profile?")
                input_profile_name = input("You: ")
                save_new_profile(input_profile_name, input_host, input_username, input_port)
            else:
                pass
            while True:
                command = input("Enter command (or 'exit' to disconnect): ")
                if command.lower() == 'exit':
                    _ssh_disconnect(ssh_client)
                    break
                stdin, stdout, stderr = ssh_client.exec_command(command)
                output = stdout.read().decode('utf-8')
                error = stderr.read().decode('utf-8')
                if output:
                    print(f"Output:\n{output}")
                if error:
                    print(f"Error:\n{error}")

#----------------------------------------Work in progress-----------------------------------
def self_connect(host,user,password):
    ssh_client = _ssh_connect(host, user, password)