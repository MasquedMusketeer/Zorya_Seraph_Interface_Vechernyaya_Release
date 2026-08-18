import pygame as pg
import os
from . import log_handler as log
from . import mood_engine_module as moem

pg.mixer.init()
audio_path = os.path.join(os.path.dirname(__file__),"Audio_lines")
talk_flag = True

def _play_audio(file_name):
    try:
        log.data_collection("AUDIO", "PLAY", f"Playing audio file: {file_name}")
        pg.mixer.music.load(os.path.join(audio_path, file_name))
        pg.mixer.music.play()
        while pg.mixer.music.get_busy():
            pg.time.delay(100)
    except FileNotFoundError:
        log.data_collection("AUDIO", "ERROR", f"Audio file not found: {file_name}")

def play_line(file_name: str):
    global talk_flag
    if talk_flag == True:
        try:
            if file_name:
                _play_audio(file_name)
        except Exception as e:
            log.data_collection("AUDIO", "ERROR", f"Error playing audio: {e}, no index matching found.")
    else:
        log.data_collection("AUDIO", "PLAY", "Talk flag is off, not playing audio.")
        
def set_talk_flag(parameter):
    global talk_flag
    talk_flag = parameter
    if talk_flag == True:
        moem.self_alter_mood_unsilence()
    elif talk_flag == False:
        moem.self_alter_mood_silence()
    log.data_collection("AUDIO", "SET TALK FLAG", f"Talk flag set to {parameter}")
    
def return_talk_flag():
    global talk_flag
    return talk_flag