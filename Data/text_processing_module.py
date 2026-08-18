import re
from . import log_handler as log
#_________________________________________________________________________________________________________________________
#__________________________________________________TEXT FORMAT HANDLER____________________________________________________
def clean_text(text_line: str):
    small_text = "Zorya: "
    big_text = []
    processing_line = text_line
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
    "                                    │            ZORYA VIGIL PROTOCOL          │",
    "                                    │           Designation: M.I.D.A.S.        │",
    "                                    ├──────────────────────────────────────────┤",
    "                                    │       Virtual assistant and banter       │",
    "                                    │          companion for your pc.          │",
    "                                    │                                          │",
    f"                                    │              Ver {mfl.flag_return("app_version")} {mfl.flag_return("development_state")}              │",
    "                                    │            Vechernyaya release           │",
    "                                    │                                          │",
    "                                    │Mendoukusai ByteLabs   All Rights Reserved│",
    "                                    └──────────────────────────────────────────┘",
    "",
    ""
    ]
    return interface_title

# """
#  ██████╗    ██████╗   ██████╗     ██████╗
#  ╚════██╗  ██╔═══██╗  ██╔═══██╗ ██╔═══██║
#   █████╔╝  ██║   ██║  ██████╔╝  ╚═██████║
#  ╚════██╗  ██║   ██║  ██╔═══╝   ██╔═══██║
#  ██████╔╝  ╚██████╔╝  ██║       ██║   ██║
#  ╚═════╝    ╚═════╝   ╚═╝       ╚═╝   ╚═╝
# """

#_________________________________________________________________________________________________________________________
#________________________________________________UNSPOKEN TEXT HANDLER____________________________________________________