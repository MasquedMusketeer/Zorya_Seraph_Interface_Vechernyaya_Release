from . import (
    command_runner as cmr,
    log_handler as log,
    memory_flags_loader as mfl,
    mood_engine_module as moem
)
import os
import subprocess


def self_backup_memory_folder():
    try:
        mfl.flag_update("last_backup_session_ID",log.sessionID_return())
        mfl.flag_update("make_backup", False)
        moem.self_alter_mood_feeling_useful()
        mfl.save_ram_flags()
        memory_folder = os.path.join(os.path.dirname(__file__), "Long_term_memory")
        appdata = os.getenv("APPDATA")
        backup_folder = os.path.join(appdata, "Zorya", "Memory_backup")
        if not os.path.exists(backup_folder):
            os.makedirs(backup_folder)
        result = subprocess.run(['robocopy', memory_folder, backup_folder, '/E'], capture_output=True)
        if result.returncode >= 8:
            stderr_text = result.stderr.decode('utf-8', errors='ignore').strip()
            log.data_collection("BACKUP MANAGER", "ERROR", f"Backup failed (code {result.returncode}): {stderr_text[:200]}")
        else:
            log.data_collection("BACKUP MANAGER", "BACKUP", "Memory folder backed up.")
    except Exception as e:
        log.data_collection("BACKUP MANAGER", "ERROR", f"Error backing up memory folder: {e}")
        
def self_restore_backup():
    try:
        mfl.flag_update("restore_backup", False)
        memory_folder = os.path.join(os.path.dirname(__file__), "Long_term_memory")
        appdata = os.getenv("APPDATA")
        backup_folder = os.path.join(appdata, "Zorya", "Memory_backup")
        if not os.path.exists(backup_folder):
            os.makedirs(backup_folder)
        result = subprocess.run(['robocopy', backup_folder, memory_folder, '/E'], capture_output=True)
        if result.returncode >= 8:
            stderr_text = result.stderr.decode('utf-8', errors='ignore').strip()
            log.data_collection("BACKUP MANAGER", "ERROR", f"Restore failed (code {result.returncode}): {stderr_text[:200]}")
        else:
            log.data_collection("BACKUP MANAGER", "RESTORE", "Memory folder restored.")
    except Exception as e:
        log.data_collection("BACKUP MANAGER", "ERROR", f"Error restoring memory folder: {e}")
    
def backup_handler(backup_indicator):
    try:
        if backup_indicator == "BACKUP":
            mfl.flag_update("make_backup", True)
        elif backup_indicator == "RESTORE":
            mfl.flag_update("restore_backup", True)
    except Exception as e:
        log.data_collection("BACKUP MANAGER", "ERROR", f"Error handling backup: {e}")