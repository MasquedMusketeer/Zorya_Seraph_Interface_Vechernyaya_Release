import json
import os
import time
import datetime as dt
from tkinter import messagebox as popup

from . import log_handler as log
from . import mood_engine_module as moem

json_path = os.path.join(os.path.dirname(__file__), "Long_term_memory", "schedule_library.json")
schedule_library = {}

#__________________________________________________________________________________________________
#_________________________________SHCEDULE LIBRARY HANDLER_________________________________________
def load_schedule_library():
    try:
        global schedule_library
        global json_path
        with open(json_path) as json_file:
            schedule_library = json.load(json_file)
        return ("Schedule library loaded", 0)
    except FileNotFoundError:
        return ("Schedule library file not found", 1)
    except json.JSONDecodeError as e:
        return ("Malformed schedule library file", 1)

def save_schedule_library():
    try:
        global schedule_library
        global json_path
        with open(json_path, "w") as json_file:
            json.dump(schedule_library, json_file, indent=4)
            log.data_collection("TASK SCHEDULER","SAVE SCHEDULE","Schedule dictionary saved on disk from memory.")
    except Exception as e:
        log.data_collection("TASK SCHEDULER","ERROR",f"Error saving schedule to disk: {e}")
#__________________________________________________________________________________________________
#_______________________________________SHCEDULE HANDLER___________________________________________
def add_schedule(_):
    try:
        global schedule_library
        #-------------------------------user required input
        schedule_ID = hex(len(schedule_library) + 1).upper().replace("0X", "$")
        print("Zorya: What's the name of the schedule?")
        schedule_name = str(input("You: ")).upper()
        print("Zorya: What's the description?")
        schedule_description = str(input("You: ")).strip() or "No description provided"
        print("Zorya: What's the category (for grouping)")
        schedule_category = str(input("You: ")).upper() or "GENERAL"
        print("Zorya: What's the due date? (YYYY-MM-DD)")
        schedule_due_date = str(input("You: ")).strip()
        print("Zorya: How often should it repeat? (none/daily/weekly/monthly/yearly)")
        schedule_repeat = str(input("You: ")).strip().lower() or "none"
        print("Zorya: How many days in advance should I remind you?")
        schedule_remind_treshold = int(input("You: ").strip() or 0)
        print("Zorya: At what time of the day should I notify you? (HH:MM:SS)")
        schedule_notification_day_time = str(input("You: ")).strip() or "12:30:00"
        #-------------------------------automatic generated information
        schedule_status = "waiting"
        schedule_notification_message = f"Reminder: {schedule_name} is due on {schedule_due_date}."
        schedule_last_notified = None
        schedule_notifications_sent = 0
        #-------------------------------schedule assembly
        schedule_library.update({
                schedule_ID: {
                    "name": schedule_name,
                    "description": schedule_description,
                    "category": schedule_category,
                    "due_date": schedule_due_date,
                    "repeat": schedule_repeat,
                    "remind_treshold": schedule_remind_treshold,
                    "notification_day_time": schedule_notification_day_time,
                    "notification_message": schedule_notification_message,
                    "status": schedule_status,
                    "last_notified": schedule_last_notified,
                    "notifications_sent": schedule_notifications_sent
            }
        })
        save_schedule_library()
        log.data_collection("TASK SCHEDULER","ADD SCHEDULE",f"New schedule added: {schedule_ID} - {schedule_name}")
        print(f"Zorya: Schedule '{schedule_name}' added successfully with ID {schedule_ID}.")
        moem.self_alter_mood_feeling_useful()
    except Exception as e:
        log.data_collection("TASK SCHEDULER","ERROR",f"Error adding new schedule: {e}")

def remove_schedule(parameter_list):
    try:
        global schedule_library
        trigger_flag = parameter_list[0]
        if trigger_flag == "usr":
            print("Zorya: Please provide the Schedule ID to remove: (format: abc123)")
            for id in schedule_library:
                print(f"- {id}: {schedule_library[id]['name']}")
            schedule_ID = "$" + input("You: ").upper()
            if schedule_ID in list(schedule_library.keys()):
                print(f"Zorya: Schedule ID: {id}: {schedule_library[id]['name']} removed from scheduler.")
                del schedule_library[schedule_ID]
                log.data_collection("TASK SCHEDULER","REMOVE SCHEDULE",f"Schedule removed: {schedule_ID}, user requested.")
            else:
                print("Zorya: The ID provided is not valid, try again numbskull.")
                return
        elif trigger_flag == "sys":
            schedule_ID = parameter_list[1]
        if schedule_ID in list(schedule_library.keys()):
            del schedule_library[schedule_ID]
            log.data_collection("TASK SCHEDULER","REMOVE SCHEDULE",f"Schedule removed: {schedule_ID}, triggered by system.")
        save_schedule_library()
    except Exception as e:
        log.data_collection("TASK SCHEDULER","ERROR",f"Error removing schedule: {e}")
#__________________________________________________________________________________________________
#______________________________________SHCEDULE NOTIFIER___________________________________________
def due_schedule_finder():
    try:
        global schedule_library
        for sch_id, sch_data in schedule_library.items():
            if sch_data["status"] == "waiting":
                due_date = dt.datetime.strptime(sch_data["due_date"], "%Y-%m-%d").date()
                current_date = dt.datetime.now().date()
                remind_treshold = dt.timedelta(days=sch_data["remind_treshold"])
                if current_date >= (due_date - remind_treshold):
                    sch_data["status"] = "due"
                    log.data_collection("TASK SCHEDULER","DUE SCHEDULE FOUND",f"Schedule due: {sch_id} - {sch_data['name']}")
        save_schedule_library()
    except Exception as e:
        log.data_collection("TASK SCHEDULER","ERROR",f"Error finding due schedules: {e}")

def notify_due_schedules(stop_event):
    try:
        while not stop_event.is_set():
            global schedule_library
            if schedule_library != {}:
                for sch_id, sch_data in schedule_library.items():
                    if sch_data["status"] == "due":
                        current_time = dt.datetime.now().time()
                        notify_time = dt.datetime.strptime(sch_data["notification_day_time"], "%H:%M:%S").time()
                        if current_time >= notify_time:
                            popup.showinfo(sch_data["name"],sch_data["notification_message"])
                            log.data_collection("TASK SCHEDULER","NOTIFY SCHEDULE",f"Notified user of due schedule: {sch_id} - {sch_data['name']}")
                            sch_data["notifications_sent"] += 1
                            sch_data["last_notified"] = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            if sch_data["remind_treshold"] <= sch_data["notifications_sent"]:
                                if sch_data["repeat"] == "none":
                                    sch_data["status"] = "completed"
                                else:
                                    sch_data["status"] = "waiting"
                                    #-------------------------------Update due date based on repeat frequency
                                    due_date = dt.datetime.strptime(sch_data["due_date"], "%Y-%m-%d").date()
                                    if sch_data["repeat"] == "daily":
                                        new_due_date = due_date + dt.timedelta(days=1)
                                    elif sch_data["repeat"] == "weekly":
                                        new_due_date = due_date + dt.timedelta(weeks=1)
                                    elif sch_data["repeat"] == "monthly":
                                        new_due_date = due_date + dt.timedelta(days=30)
                                    elif sch_data["repeat"] == "yearly":
                                        new_due_date = due_date + dt.timedelta(days=365)
                                    sch_data["due_date"] = new_due_date.strftime("%Y-%m-%d")
                                    sch_data["notification_message"] = f"Reminder: {sch_data["name"]} is due on {sch_data["due_date"]}."
            save_schedule_library()
            time.sleep(3600)
    except Exception as e:
        log.data_collection("TASK SCHEDULER","ERROR",f"Error notifying due schedules: {e}")

def schedule_library_sanitizer():
    try:
        global schedule_library
        schedules_to_remove = []
        for sch_id, sch_data in schedule_library.items():
            if sch_data["status"] == "completed":
                schedules_to_remove.append(sch_id)
        for sch_id in schedules_to_remove:
            remove_schedule(["sys",sch_id])
            log.data_collection("TASK SCHEDULER","SANITIZE SCHEDULE LIBRARY",f"Removed completed schedule: {sch_id}")
        save_schedule_library()
    except Exception as e:
        log.data_collection("TASK SCHEDULER","ERROR",f"Error sanitizing schedule library: {e}")