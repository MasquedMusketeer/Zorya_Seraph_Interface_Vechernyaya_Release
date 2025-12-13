import os
import re
import json
from . import log_handler as log
text_buffer = {}
text_file_path = os.path.join(os.path.dirname(__file__),"Long_term_memory", "text_lines.json")

def load_text_file():
    global text_buffer
    try:
        with open(text_file_path, 'r', encoding='utf-8') as text_file:
            text_buffer = json.load(text_file)
        return ("Text file loaded", 0)
    except FileNotFoundError:
        log.data_collection("TEXT", "ERROR", "Text index file not found.")
        return ("Bad text file path", 1)

def clean_text(category: str, line:str ):
    small_text = "Zorya: "
    big_text = []
    global text_buffer
    processing_line = text_buffer.get(category).get(line)
    if "/" in processing_line:
        parts = processing_line.split("/") 
        big_text.append("MULTILINE")
        big_text.append("Zorya: ")
        for part in parts:
            part = re.sub(r'^\s*\[?\d+\]?\s*[\.\-\)\/:]?\s*', '', part)
            big_text.append(part)
        log.data_collection("TEXT", "CALL TEXT", f"Processed line: {big_text}")
        return big_text
    else :
        parts = processing_line
        for part in parts:
            part = re.sub(r'^\s*\[?\d+\]?\s*[\.\-\)\/:]?\s*', '', part)
            small_text += part
        log.data_collection("TEXT", "CALL TEXT", f"Processed line: {small_text.strip("\n")}")
        return small_text

def header_return():
    from . import memory_flags_loader as mfl
    interface_title = [
    "                                     ███████╗ ██████╗ ██████╗ ██╗   ██╗ █████╗",
    "                                     ╚══███╔╝██╔═══██╗██╔══██╗╚██╗ ██╔╝██╔══██╗",
    "                                       ███╔╝ ██║   ██║██████╔╝ ╚████╔╝ ███████║",
    "                                      ███╔╝  ██║   ██║██╔══██╗  ╚██╔╝  ██╔══██║",
    "                                     ███████╗╚██████╔╝██║  ██║   ██║   ██║  ██║",
    "                                     ╚══════╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝",
    "                                    ┌──────────────────────────────────────────┐",
    "                                    │         ZORYA SERAPH INTERFACE           │",
    "                                    ├──────────────────────────────────────────┤",
    "                                    │       Virtual assistant and banter       │",
    "                                    │          companion for your pc.          │",
    "                                    │                                          │",
    f"                                    │             Ver {mfl.flag_return("app_version")} {mfl.flag_return("development_state")}              │",
    "                                    │           Vechernyaya release            │",
    "                                    │                                          │",
    "                                    │Mendoukusai ByteLabs   All Rights Reserved│",
    "                                    └──────────────────────────────────────────┘",
    "",
    ""
    ]
    return interface_title