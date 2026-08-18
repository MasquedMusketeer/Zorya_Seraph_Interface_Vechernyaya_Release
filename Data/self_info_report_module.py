from . import (
    log_handler as log,
    memory_flags_loader as mfl,
    audio_play_module as apm,
    interpretation_engine as interpreter,
    bootstrapper as boot,
    response_handler as rph
)
import time

def respond_time_query(_):
    response = (
        f"-------------------------------\n"
        f"Current time: {time.strftime('%H:%M:%S')}\n"
        f"-------------------------------"
    )
    return response

def self_report_last_backup(_):
    current_session_ID = log.sessionID_return()
    last_backup_session_ID = mfl.flag_return("last_backup_session_ID")
    response = (
        f"-------------------------------\n"
        f"  Last backup session ID: {last_backup_session_ID}\n"
        f"  Current session ID: {current_session_ID}\n"
        f"-------------------------------"
    )
    return response

def report_self_status(_):
    startup_errors = mfl.flag_return("startup_errors")
    talk_flag = apm.return_talk_flag()
    talk_status = "Zorya is set to talk." if talk_flag else "Zorya is set to silent."
    self_mood = mfl.flag_return('self_mood_score')
    mood_lines = "\n".join([f"{key}: {self_mood[key]}" for key in self_mood])
    system_status = "All systems nominal." if startup_errors == 0 else "Errors on execution,\nrefer to logs for details."
    
    response = (
        f"-------------------------------\n"
        f"    Zorya current status\n"
        f"-------------------------------\n"
        f"Session ID: {log.sessionID_return()}\n"
        f"Startup errors: {startup_errors}\n"
        f"{talk_status}\n"
        f"Current mood score:\n"
        f"{mood_lines}\n"
        f"Operator mood score: {mfl.flag_return('operator_mood_score')}\n"
        f"{boot.memory_usage()}\n"
        f"{system_status}\n"
        f"-------------------------------"
    )
    log.data_collection("ZORYA", "REPORT", f"talk_flag: {talk_flag},Current mood score: {mfl.flag_return('self_mood_score')},Operator mood score: {mfl.flag_return('operator_mood_score')},Startup errors: {startup_errors}")
    return response

def self_query_intent_report(_):
    response = (
        f"-------------------------------\n"
        f"    My current intents: {len(interpreter.intent_map)}\n"
        f"-------------------------------"
    )
    return response

def self_recent_log_report(_):
    recent_logs = log.show_recent_logs()
    response = "\n".join([logs for logs in recent_logs if logs != ""])
    return response

def respond_self_query(_):
    try:
        self_mood_score = mfl.flag_return("self_mood_score")
        highest_mood = max(self_mood_score, key=self_mood_score.get)
        if highest_mood == "happy":
            rph.audio_text_synchronizer("HAPPY")
        elif highest_mood == "neutral":
            rph.audio_text_synchronizer("MILD")
        elif highest_mood == "sad":
            rph.audio_text_synchronizer("SAD")
    except Exception as e:
        log.data_collection("ZORYA", "ERROR", f"Error in response: {e}")