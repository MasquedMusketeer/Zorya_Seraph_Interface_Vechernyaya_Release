import tkinter as tk
import os
import time
from . import (
    memory_flags_loader as mfl,
    log_handler as log
)

info_dict = {}
#________________________________________________________________________________________________________
#_____________________________________INFO GATHER________________________________________________________
def info_dict_populator():
    try:
        if info_dict:
            info_dict.clear()
        info_dict.update(mfl.state_return())
    except Exception as e:
        log.data_collection("DASHBOARD", "ERROR", f"Error populating info dict: {e}")
#________________________________________________________________________________________________________
#_____________________________________DASHBOARD HANDLER__________________________________________________
def launch_dashboard(stop_event):
    time.sleep(15)
    style_config = mfl.flag_return("dashboard_config")
    zorya_icon = os.path.join(os.path.dirname(__file__), "icon", "Zorya.ico")
    info_dict_populator()
#________________________________________________________________________________________________________
#_____________________________________DASHBOARD INIT_____________________________________________________
    main_window = tk.Tk()
    main_window.title("Zorya Status Display")
    main_window.geometry("300x550")
    main_window.configure(bg=style_config["bg_color"])
    
    try:
        main_window.tk.call("tk", "windowingsystem")
        main_window.tk.call("set", "::tk::mac::useThemedToplevel", "1")
        main_window.attributes("-alpha", 0.0)
        main_window.update()
        main_window.attributes("-alpha", 1.0)
        import ctypes
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            ctypes.windll.user32.GetParent(main_window.winfo_id()), 
            20, 
            ctypes.byref(ctypes.c_int(2)), 
            ctypes.sizeof(ctypes.c_int)
        )
    except:
        pass
    try:
        main_window.lift()
        main_window.attributes("-topmost", True)
        main_window.iconbitmap(zorya_icon)
        
        main_frame = tk.Frame(main_window, bg="#100A00")
        main_frame.pack(side=tk.TOP, fill=tk.BOTH)
#________________________________________________________________________________________________________
#___________________________________________TITLE LABEL__________________________________________________        
        title_label = tk.Label(
            main_frame, 
            text="Zorya Status Display", 
            bg=style_config["bg_color"], 
            fg=style_config["title_font_color"], 
            font=(style_config["font_type"], style_config["title_font_size"], "bold")
        )
        title_label.pack(pady=10)
#________________________________________________________________________________________________________
#____________________________________________BODY LABEL__________________________________________________         
        current_session_ID_label = tk.Label(
            main_frame, 
            text=f"✦ Current sessionID: {hex(info_dict['session_count'] - 1).upper().replace('0X', '$')}", 
            bg=style_config["bg_color"], 
            fg=style_config["label_font_color"], 
            font=(style_config["font_type"], style_config["label_font_size"]),
            anchor="w"
        )
        current_session_ID_label.pack(pady=3, fill="x", padx=10)

        last_backup_session_ID_label = tk.Label(
            main_frame, 
            text=f"✦ Last backup sessionID: {info_dict['last_backup_session_ID']}", 
            bg=style_config["bg_color"], 
            fg=style_config["label_font_color"], 
            font=(style_config["font_type"], style_config["label_font_size"]),
            anchor="w"
        )
        last_backup_session_ID_label.pack(pady=3, fill="x", padx=10)
        
        startup_errors_label = tk.Label(
            main_frame, 
            text=f"✦ Startup errors: {info_dict['startup_errors']}", 
            bg=style_config["bg_color"], 
            fg=style_config["label_font_color"], 
            font=(style_config["font_type"], style_config["label_font_size"]),
            anchor="w"
        )
        startup_errors_label.pack(pady=3, fill="x", padx=10)
        current_mode = ("API" if info_dict["api_mode"] == True else "CLI")
        api_mode_label = tk.Label(
            main_frame, 
            text=f"✦ Execution mode: {current_mode}", 
            bg=style_config["bg_color"], 
            fg=style_config["label_font_color"], 
            font=(style_config["font_type"], style_config["label_font_size"]),
            anchor="w"
        )
        api_mode_label.pack(pady=3, fill="x", padx=10)
        
        self_mood_score = info_dict["self_mood_score"]
        highest_mood = max(self_mood_score, key=self_mood_score.get)
        self_mood_score_label = tk.Label(
            main_frame, 
            text=f"✦ Mood: {highest_mood.capitalize()} | {self_mood_score[highest_mood]}", 
            bg=style_config["bg_color"], 
            fg=style_config["label_font_color"], 
            font=(style_config["font_type"], style_config["label_font_size"]),
            anchor="w"
        )
        self_mood_score_label.pack(pady=3, fill="x", padx=10)
#________________________________________________________________________________________________________
#____________________________________________FRAME LABEL_________________________________________________        
        startup_label_frame = tk.Frame(main_frame, bg=style_config["bg_color"])
        apps_expected_at_start_label = tk.Label(
            startup_label_frame, 
            text="✦ Startup apps:", 
            bg=style_config["bg_color"], 
            fg=style_config["label_font_color"], 
            font=(style_config["font_type"], style_config["label_font_size"]),
            anchor="w"
        )
        apps_expected_at_start_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=3)
        for i, app in enumerate(info_dict["apps_expected_at_start"]):
            row = (i // 2) + 1
            col = i % 2
            tk.Label(
                startup_label_frame,
                text=f"   ●{app}",
                bg=style_config["bg_color"],
                fg=style_config["label_font_color"],
                font=(style_config["font_type"], style_config["lable_subtext_font_size"]),
                anchor="w"
            ).grid(row=row, column=col, sticky="w", padx=10, pady=1)
        startup_label_frame.pack(pady=3, fill="x")
        
        recent_apps_label_frame = tk.Frame(main_frame, bg=style_config["bg_color"])
        apps_recently_used_label = tk.Label(
            recent_apps_label_frame, 
            text="✦ Tracking apps:", 
            bg=style_config["bg_color"], 
            fg=style_config["label_font_color"], 
            font=(style_config["font_type"], style_config["label_font_size"]),
            anchor="w"
        )
        apps_recently_used_label.pack(pady=3, fill="x", padx=10)
        for app, value in info_dict["apps_recently_used"].items():
            tk.Label(
                recent_apps_label_frame,
                text=f"   {app} : {value}",
                bg=style_config["bg_color"],
                fg=style_config["label_font_color"],
                font=(style_config["font_type"], style_config["lable_subtext_font_size"]),
                anchor="w"
            ).pack(pady=1, fill="x", padx=10)
        recent_apps_label_frame.pack(pady=3, fill="x")
        
        alert_label_frame = tk.Frame(main_frame, bg=style_config["bg_color"])
        system_alert_threshold_flag_label = tk.Label(
            alert_label_frame, 
            text="⚠️ System alert parameters:", 
            bg=style_config["bg_color"], 
            fg=style_config["label_font_color"], 
            font=(style_config["font_type"], style_config["label_font_size"]),
            anchor="w"
        )
        system_alert_threshold_flag_label.pack(pady=3, fill="x", padx=10)
        
        system_alert_notification_mute_flag = info_dict["system_alert_notification_mute_flag"]
        system_alert_threshold_flag = info_dict["system_alert_threshold_flag"]
        parameter_list = []
        for flag, value in system_alert_threshold_flag.items():
            parameter_list.append(f"{flag} : {value}")
        for flag, value in system_alert_notification_mute_flag.items():
            parameter = parameter_list.pop(0)
            value_str = "Muted" if value else "Active"
            parameter_list.append(f"{parameter} | {value_str}")
        for parameter in parameter_list:
            tk.Label(
                alert_label_frame,
                text=f"   {parameter}",
                bg=style_config["bg_color"],
                fg=style_config["label_font_color"],
                font=(style_config["font_type"], style_config["lable_subtext_font_size"]),
                anchor="w"
            ).pack(pady=1, fill="x", padx=10)
        alert_label_frame.pack(pady=3, fill="x")
#________________________________________________________________________________________________________
#___________________________________________FOOTER LABEL_________________________________________________        
        footer_label = tk.Label(
            main_window, 
            text=f"v{mfl.flag_return("app_version")} {mfl.flag_return("development_state")} | Utrennyaya",
            bg=style_config["bg_color"],
            fg=style_config["label_font_color"],
            font=(style_config["font_type"], style_config["footer_font_size"])
        )
        footer_label.pack(side=tk.BOTTOM)
#________________________________________________________________________________________________________
#__________________________________________REFRESH LABELS________________________________________________        
        def update_labels():
            if stop_event.is_set():
                main_window.destroy()
                return
                
            info_dict_populator()
            
            current_session_ID_label.config(text=f"✦ Current sessionID: {hex(info_dict['session_count'] - 1).upper().replace('0X', '$')}")
            last_backup_session_ID_label.config(text=f"✦ Last backup sessionID: {info_dict['last_backup_session_ID']}")
            startup_errors_label.config(text=f"✦ Startup errors: {info_dict['startup_errors']}")
            api_mode_label.config(text=f"✦ Execution mode: {"API" if info_dict["api_mode"] == True else "CLI"}")
            
            self_mood_score = info_dict["self_mood_score"]
            highest_mood = max(self_mood_score, key=self_mood_score.get)
            self_mood_score_label.config(text=f"✦ Mood: {highest_mood.capitalize()} | {self_mood_score[highest_mood]}")
            
            for widget in startup_label_frame.winfo_children()[1:]:
                widget.destroy()
            for i, app in enumerate(info_dict["apps_expected_at_start"]):
                row = (i // 2) + 1
                col = i % 2
                tk.Label(startup_label_frame, text=f"   ●{app}", bg=style_config["bg_color"], 
                        fg=style_config["label_font_color"], font=(style_config["font_type"], style_config["lable_subtext_font_size"]), 
                        anchor="w").grid(row=row, column=col, sticky="w", padx=10, pady=1)
            
            for widget in recent_apps_label_frame.winfo_children()[1:]:
                widget.destroy()
            for app, value in info_dict["apps_recently_used"].items():
                tk.Label(recent_apps_label_frame, text=f"   {app} : {value}", bg=style_config["bg_color"], 
                        fg=style_config["label_font_color"], font=(style_config["font_type"], style_config["lable_subtext_font_size"]), 
                        anchor="w").pack(pady=1, fill="x", padx=10)

            for widget in alert_label_frame.winfo_children()[1:]:
                widget.destroy()
            system_alert_notification_mute_flag = info_dict["system_alert_notification_mute_flag"]
            system_alert_threshold_flag = info_dict["system_alert_threshold_flag"]
            parameter_list = []
            for flag, value in system_alert_threshold_flag.items():
                parameter_list.append(f"{flag} : {value}")
            for flag, value in system_alert_notification_mute_flag.items():
                parameter = parameter_list.pop(0)
                value_str = "Muted" if value else "Active"
                parameter_list.append(f"{parameter} | {value_str}")
            for parameter in parameter_list:
                tk.Label(alert_label_frame, text=f"   {parameter}", bg=style_config["bg_color"], 
                        fg=style_config["label_font_color"], font=(style_config["font_type"], style_config["lable_subtext_font_size"]), 
                        anchor="w").pack(pady=1, fill="x", padx=10)
            
            main_window.after(30000, update_labels)
        
        update_labels()
        main_window.mainloop()
    except Exception as e:
        log.data_collection("DASHBOARD", "ERROR", f"Error displaying system info: {e}")
