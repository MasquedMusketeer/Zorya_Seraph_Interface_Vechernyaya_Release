import os
from winotify import Notification, audio
from datetime import datetime

_log_path = os.path.join(os.path.dirname(__file__), "Logs")
last_log_entry = ""

sessionID = "$00"

def _log_registration(message: str):
    os.makedirs(_log_path, exist_ok=True)
    log_file_path = os.path.join(_log_path, "general_system_log.txt")
    with open(log_file_path, "a", encoding="utf-8") as log_file:
        log_file.write(message + "\n")

def _log_builder(_log_data):
    global sessionID
    global last_log_entry
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status, action, details = _log_data
    log_entry = f"[{timestamp}] [{sessionID}] [{status}] [{action}] {details}"
    last_log_entry = log_entry
    if "[ERROR]" in last_log_entry:
        notification_message = f"[{status}] [{action}] {details}"
        log_notifier(notification_message)
    _log_registration(log_entry.strip("\n"))

def data_collection(_data_type: str, _action: str, _details: str):
    _log_builder([_data_type, _action, _details])

def session_setter(s_id: str):
    global sessionID
    sessionID = s_id.upper().replace("0X", "$")

def sessionID_return():
    global sessionID
    return sessionID

def show_recent_logs():
    recent_log = []
    log_file_path = os.path.join(_log_path, "general_system_log.txt")
    with open(log_file_path, "r", encoding="utf-8") as log_file:
        log_content = log_file.readlines()
        for line in log_content[-20:]:
            recent_log.append(line.strip("\n"))
    return recent_log

def log_clean():
    log_header = [
        "Zorya General System Log",
        "──────────────────────────────────────────────────────────────────────────────────────────────────────────────",
        "[TIMESTAMP] [SESSIONID] [STATUS] [ACTION] [DETAILS]"
    ]
    log_file_path = os.path.join(_log_path, "general_system_log.txt")
    try:
        with open(log_file_path, "w", encoding="utf-8") as log_file:
            for line in log_header:
                log_file.write(line + "\n")
    except Exception as e:
        print(f"Error cleaning log: {e}")
        
def count_log_lines():
    log_file_path = os.path.join(_log_path, "general_system_log.txt")
    try:
        with open(log_file_path, "r", encoding="utf-8") as log_file:
            return sum(1 for _ in log_file)
    except Exception as e:
        data_collection("LOG", "ERROR", f"Error counting log lines: {e}")
        return 0
         
def log_notifier(message: str):
    try:
        Zorya_icon = os.path.join(os.path.dirname(__file__), "icon", "Zorya.ico")
        toast = Notification(app_id="Zorya.System",title="Error",msg=message,icon=Zorya_icon)
        toast.set_audio(audio.Default, loop=False)
        toast.show()
    except Exception as e:
        data_collection("LOG", "ERROR", f"Notification failed: {e}")