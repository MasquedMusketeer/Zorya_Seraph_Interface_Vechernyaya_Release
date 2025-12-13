import os
import sys
import time
import json
import psutil
import threading as parallel
#import Data.log_handler as log


def _get_all_running_processes():
    try:
        processes = []
        for proc in psutil.process_iter(['name']):
            try:
                if proc.name() not in processes:
                    processes.append(proc.name())
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return processes
    except Exception as e:
        #log.data_collection("SYSTEM", "PROCESS", f"Error getting all running processes: {e}")
        return []

print(_get_all_running_processes())