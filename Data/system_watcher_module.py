import os
import time
import json
import win32gui
import win32process
from win32com.shell import shell #type:ignore
import psutil
import threading as parallel
from . import (
    log_handler as log,
    memory_flags_loader as mfl
)

download_folder_path = os.path.join(os.environ['USERPROFILE'], 'Downloads')
_complete_system_info = None
_system_info_lock = parallel.Lock()
wgb_file_path = os.path.join(os.path.dirname(__file__), "Long_term_memory", "app_white_grey_blacklist.json")
wgb_app_list = {}
#_________________________________________________________________________________________________________________________
#____________________________________________________ASSETS HANDLER_______________________________________________________
def load_wgb_list():
    try:
        global wgb_app_list
        global wgb_file_path
        with open (wgb_file_path) as wgb_file:
            wgb_app_list = json.load(wgb_file)
        return ("Apps Blacklist loaded", 0)
    except FileNotFoundError:
        log.data_collection("SYSTEM WATCHER", "ERROR", "Apps Blacklist file not found.")
        return ("Bad audio file path", 1)
    except json.JSONDecodeError as e:
        log.data_collection("SYSTEM WATCHER", "ERROR", f"JSON parse error: {e}")
        return ("Malformed Apps Blacklist file", 1)
def save_new_wgb_app(category: str, app: str):
    try:
        global wgb_app_list
        global wgb_file_path
        if category not in wgb_app_list:
            wgb_app_list[category] = []
        if app not in wgb_app_list[category]:
            wgb_app_list[category].append(app)
        with open(wgb_file_path, "w") as wgb_file:
            json.dump(wgb_app_list, wgb_file, indent=4)
    except Exception as e:
        log.data_collection("SYSTEM WATCHER", "ERROR", f"Error saving new wgb app: {e}")
        return None
#_________________________________________________________________________________________________________________________
#_____________________________________________SYSTEM LEVEL INFO GATHERER__________________________________________________
def _get_processes_grouped_by_name():
    processes = {}
    try:
        for proc in psutil.process_iter([
            'pid',
            'name',
            'exe',
            'cmdline',
            'username',
            'ppid'
        ]):
            try:
                info = proc.info
                name = info.pop('name', None)
                pid = info.get('pid')
                if not name or pid is None:
                    continue
                if name not in processes:
                    processes[name] = {}
                # Use PID as the sub-key
                processes[name][pid] = {
                    'exe': info.get('exe'),
                    'cmdline': info.get('cmdline'),
                    'username': info.get('username'),
                    'ppid': info.get('ppid')
                }
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return processes
    except Exception as e:
        log.data_collection("SYSTEM WATCHER", "ERROR", f"Error getting processes: {e}")
        return None

def _get_visible_apps():
    apps = []
    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
            try:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                proc = psutil.Process(pid)
                app_name = proc.name()
                window_title = win32gui.GetWindowText(hwnd)
                apps.append((app_name, window_title))
            except Exception:
                log.data_collection("SYSTEM WATCHER", "ERROR", f"Error getting process info for window: {hwnd}")
        return True

    win32gui.EnumWindows(callback, None)
    unique = {}
    for name, title in apps:
        if name not in unique:
            unique[name] = title
    user_apps = []
    for name in unique:
        name_without_ext = name[:-4] if name.lower().endswith(".exe") else name
        user_apps.append(name_without_ext.lower())
    return user_apps

def _get_disk_usage():
    disks = {}
    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
            mount = part.mountpoint.rstrip("\\/")
            disks[mount] = {
                "percentage": usage.percent,
                "free": usage.free
            }
        except (PermissionError, FileNotFoundError):
            continue
    return disks

def _get_system_level_resource_info():
    global _complete_system_info
    try:
        net = psutil.net_io_counters()
        system_info = {
            'cpu_usage': psutil.cpu_percent(interval=None),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': _get_disk_usage(),
            'network_usage': net.bytes_sent + net.bytes_recv
        }
        with _system_info_lock:
            _complete_system_info = system_info
    except Exception as e:
        log.data_collection("SYSTEM WATCHER", "ERROR", f"Error getting system info: {e}")
        return None
#_________________________________________________________________________________________________________________________
#______________________________________________TRASH STATE INFO GATHERER__________________________________________________
def _computer_trash_info_gather():
    try:
        trash_bin_state = shell.SHQueryRecycleBin()
        trash_bin_total_size = trash_bin_state[0] / 1024**2
        trash_bin_file_ammount = trash_bin_state[1]
        return trash_bin_total_size, trash_bin_file_ammount
    except Exception as e:
        log.data_collection("SYSTEM WATCHER", "ERROR", f"Error getting trash info: {e}")
        return None

def get_trash_size():
    try:
        trash_info = _computer_trash_info_gather()
        if trash_info:
            return trash_info[0]
    except Exception as e:
        log.data_collection("SYSTEM WATCHER", "ERROR", f"Error getting trash size: {e}")
        return None
#_________________________________________________________________________________________________________________________
#____________________________________________DOWNLOAD STATE INFO GATHERER_________________________________________________
def _download_info_gather():
    try:
        download_state = os.listdir(download_folder_path)
        download_file_count = len(download_state)
        return download_file_count
    except Exception as e:
        log.data_collection("SYSTEM WATCHER", "ERROR", f"Error getting download info: {e}")
        return None

def get_download_file_count():
        try:
            download_info = _download_info_gather()
            if download_info:
                return download_info
        except Exception as e:
            log.data_collection("SYSTEM WATCHER", "ERROR", f"Error getting download count: {e}")
            return None
#_________________________________________________________________________________________________________________________
#________________________________________________SYSTEM INFO HANDLER______________________________________________________
def return_system_info():
    try:
        with _system_info_lock:
            return _complete_system_info.copy()
    except Exception as e:
        log.data_collection("SYSTEM WATCHER", "ERROR", f"Error returning system info: {e}")
        return None

def system_info_updater(stop_event):
    try:
        while not stop_event.is_set():
            _get_system_level_resource_info()
            time.sleep(10)
    except Exception as e:
        log.data_collection("SYSTEM WATCHER", "ERROR", f"Error in system info updater: {e}")

def set_alert_config(flag_dict,flag,value):
    try:
        dict_flags = mfl.flag_return(flag_dict)
        dict_flags[flag] = value
        mfl.flag_update(flag_dict,dict_flags)
        return 0
    except Exception as e:
        log.data_collection("SYSTEM WATCHER", "ERROR", f"Error setting alert config for {flag}: {e}")
        return 1
    
def get_warning_level_running_apps(warning_level, log_frequency_counter):
    try:
        global wgb_app_list
        all_running_blacklisted_apps = []
        current_blacklist = wgb_app_list[warning_level]
        running_apps_dict_by_name = _get_processes_grouped_by_name()
        running_apps = [
            (app[:-4]).lower() if app.lower().endswith(".exe") else app.lower()
            for app in running_apps_dict_by_name.keys()
]
        if log_frequency_counter == 10:
            log.data_collection("SYSTEM WATCHER", "INFO", f"Checking for {warning_level} level apps in {running_apps}")
        for app in current_blacklist:
            if app in running_apps:
                all_running_blacklisted_apps.append(app)
        return all_running_blacklisted_apps
    except Exception as e:
        log.data_collection("SYSTEM WATCHER", "ERROR", f"Error getting current {warning_level} level running apps: {e}")
#________________________________________________________________________________________________________________________   
#__________________________________________________SYSTEM ALERT SETTER___________________________________________________   
def alert_flag_and_value_choice(_):
    print("Zorya: What you want to do? (value limit, mute/unmute)")
    usr_dict_choice = input("You: ")
    print(f"Zorya: For what parameter? ({mfl.flag_return("system_alert_threshold_flag").keys})")
    usr_flag_choice = input("You: ")
    if usr_flag_choice.lower() not in ("cpu", "ram", "disk", "trash","download"):
        usr_flag_choice = None
    if usr_dict_choice == "value limit":
        usr_dict_choice = "system_alert_threshold_flag"
        print("Zorya: What percentage (0-100) or, for trash, what size (in MB)?")
        usr_value_choice = input("You: ")
        usr_value_choice = int(usr_value_choice)
        if usr_value_choice < 0 or (usr_value_choice > 100 and usr_flag_choice != "trash"):
            usr_value_choice = None
    elif usr_dict_choice == "mute":
        usr_dict_choice = "system_alert_notification_mute_flag"
        usr_value_choice = True
    elif usr_dict_choice == "unmute":
        usr_dict_choice = "system_alert_notification_mute_flag"
        usr_value_choice = False
    else:
        usr_dict_choice = None
        usr_value_choice = None
    if usr_dict_choice == None or usr_flag_choice == None or usr_value_choice == None:
        print("Zorya: Invalid inputs were made, try again, but righjt this time...")
        return
    operation_response = set_alert_config(usr_dict_choice, usr_flag_choice, usr_value_choice)
    if operation_response == 0 and usr_dict_choice == "system_alert_threshold_flag":
        print(f"Zorya: Alert threshold of {usr_flag_choice} updated to {usr_value_choice}.")
    elif operation_response == 0 and usr_dict_choice == "system_alert_notification_mute_flag":
        print(f"Zorya: Alert notification mute of {usr_flag_choice} updated to {usr_value_choice}.")
    elif operation_response == 1:
        print(f"Zorya: Failure on updating, see logs for detail.")