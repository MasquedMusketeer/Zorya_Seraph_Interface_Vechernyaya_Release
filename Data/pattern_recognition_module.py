import psutil
import win32gui
import win32process
from . import memory_flags_loader as mfl
from . import log_handler as log


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
                log.data_collection("PATTERN RECOGNITION", "ERROR", f"Error getting process info for window: {hwnd}")
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

def query_most_used_apps():
    try:
        user_apps = _get_visible_apps()
        for app in user_apps:
            mfl.update_recently_used_apps(app, False)
        log.data_collection("PATTERN RECOGNITION", "MOST USED APPS", f"Most used apps colected: {user_apps}")
    except Exception as e:
        log.data_collection("PATTERN RECOGNITION", "ERROR", f"Error querying most used apps: {e}")

def used_apps_score_degradation():
    try:
        registered_apps = mfl.flag_return("apps_recently_used").copy()
        user_apps = _get_visible_apps()
        for app in registered_apps:
            if app not in user_apps:
                mfl.update_recently_used_apps(app, True)
    except Exception as e:
        log.data_collection("PATTERN RECOGNITION", "ERROR", f"Error updating recently used apps: {e}")

#-----------------------------------------------------------Used to gather and save new paths from frequent executables.
def get_exe_path_from_name(name):
    try:
        for proc in psutil.process_iter(['name', 'exe']):
            if proc.info['name'] and name.lower() in proc.info['name'].lower():
                log.data_collection("PATTERN RECOGNITION", "EXE PATH", f"Exe path found for {name}: {proc.info['exe']}")
                return proc.info['exe']
        return None
    except Exception as e:
        log.data_collection("PATTERN RECOGNITION", "ERROR", f"Error getting exe path from name: {e}")