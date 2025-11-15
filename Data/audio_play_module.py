try:
    import pygame as pg
except ImportError:
    print("Pygame not found, installing...")
    import pip
    pip.main(['install', 'pygame'])
    import pygame as pg
import json
import os
from . import log_handler as log

pg.mixer.init()
audio_index = {}
audio_path = os.path.join(os.path.dirname(__file__),"Audio_lines")
index_path = os.path.join(os.path.dirname(__file__),"Long_term_memory","audio_dictionary.json")
talk_flag = True

def load_audio_index():
    global audio_index
    try:
        with open(index_path, 'r', encoding='utf-8') as index_file:
            audio_index = json.load(index_file)
        return ("Audio index loaded", 0)
    except FileNotFoundError:
        log.data_collection("AUDIO", "LOAD_FILE", "Audio index file not found.")
        return ("Bad audio file path", 1)
    except json.JSONDecodeError as e:
        log.data_collection("AUDIO", "LOAD_FILE", f"JSON parse error: {e}")
        return ("Malformed audio index file", 1)

def _play_audio(file_name):
    try:
        log.data_collection("AUDIO", "PLAY", f"Playing audio file: {file_name}")
        pg.mixer.music.load(os.path.join(audio_path, file_name))
        pg.mixer.music.play()
        while pg.mixer.music.get_busy():
            pg.time.delay(100)
    except FileNotFoundError:
        log.data_collection("AUDIO", "PLAY", f"Audio file not found: {file_name}")

def play_line(category: str, index: str):
    global talk_flag
    if talk_flag == True:
        try:
            file_name = audio_index.get(category, {}).get(index)
            if file_name:
                _play_audio(file_name)
        except Exception as e:
            log.data_collection("AUDIO", "PLAY", f"Error playing audio: {e}, no index matching found.")
    else:
        log.data_collection("AUDIO", "PLAY", "Talk flag is off, not playing audio.")
        
def set_talk_flag(parameter):
    global talk_flag
    talk_flag = parameter
    log.data_collection("AUDIO", "SET TALK FLAG", f"Talk flag set to {parameter}")
    
def return_talk_flag():
    global talk_flag
    return talk_flag