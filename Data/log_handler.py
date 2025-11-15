import os
from datetime import datetime   # not datetime.now()

_log_path = os.path.join(os.path.dirname(__file__), "Logs")

sessionID = "0x00000000"

def _log_registration(message: str):
    os.makedirs(_log_path, exist_ok=True)
    log_file_path = os.path.join(_log_path, "general_system_log.txt")
    with open(log_file_path, "a", encoding="utf-8") as log_file:
        log_file.write(message + "\n")

def _log_builder(_log_data):
    global sessionID
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status, action, details = _log_data
    log_entry = f"[{timestamp}] [{sessionID}] [{status}] [{action}] {details}"
    _log_registration(log_entry.strip("/n"))

def data_collection(_data_type: str, _action: str, _details: str):
    _log_builder([_data_type, _action, _details])

def session_setter(s_id: str):
    global sessionID
    sessionID = s_id

def sessionID_return():
    global sessionID
    return sessionID
#--------------------------------------------------------------------DO NOT USE, WORK IN PROGRESS   
def log_analyzer():
    log_file_path = os.path.join(_log_path, "general_system_log.txt")
    with open(log_file_path, "r", encoding="utf-8") as log_file:
        log_content = log_file.read()
    return log_content
