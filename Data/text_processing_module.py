import os
import re
from . import log_handler as log
text_buffer = []
text_file_path = os.path.join(os.path.dirname(__file__),"text_files", "text_index.txt")

def load_text_file():
    global text_buffer
    try:
        with open(text_file_path, 'r', encoding='utf-8') as text_file:
            text_buffer = text_file.readlines()
        return ("Text file loaded", 0)
    except FileNotFoundError:
        log.data_collection("TEXT", "LOAD_FILE", "Text index file not found.")
        return ("Bad text file path", 1)

def clean_text(line):
    small_text = "Zorya: "
    big_text = []
    global text_buffer
    processing_line = text_buffer[line]
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
    
