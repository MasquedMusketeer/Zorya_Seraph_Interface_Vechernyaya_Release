from . import memory_flags_loader as mfl
from . import log_handler as log

operator_mood_score = mfl.flag_return("operator_mood_score")

def alter_self_mood(order,value):
    self_mood_score = mfl.flag_return("self_mood_score")
    mood_max_value = 2.0
    overflow = 0
    try:
        if order == "h>n>s":
            mood_high = "happy"
            mood_med = "neutral"
            mood_low = "sad"
        elif order == "s>n>h":
            mood_high = "sad"
            mood_med = "neutral"
            mood_low = "happy"
            
        if self_mood_score[mood_high]> 0:
            self_mood_score[mood_high] -= value
            if self_mood_score[mood_high] < 0:
                overflow = abs(self_mood_score[mood_high])
                self_mood_score[mood_high] = 0
                self_mood_score[mood_med] = mood_max_value - overflow
                self_mood_score[mood_low] += overflow
            self_mood_score[mood_med] += value
            
        elif self_mood_score[mood_high] == 0 and self_mood_score[mood_low] < 2:
            self_mood_score[mood_med] -= value
            if self_mood_score[mood_med] < 0:
                self_mood_score[mood_med] = 0
                self_mood_score[mood_low] = mood_max_value
            self_mood_score[mood_low] += value
        
        else:
            log.data_collection("MOOD ENGINE", "CHANGE", "No changes in the current mood were made due it it being maxed out.")
        
        self_mood_score[mood_high] = round(self_mood_score[mood_high], 1)
        self_mood_score[mood_med] = round(self_mood_score[mood_med], 1)
        self_mood_score[mood_low] = round(self_mood_score[mood_low], 1)
        mfl.flag_update("self_mood_score", self_mood_score)
    except Exception as e:
        log.data_collection("MOOD ENGINE", "ERROR", f"Error altering self mood: {e}")
        
        
def raise_mood(value):
    alter_self_mood("s>n>h", value)
    log.data_collection("MOOD ENGINE", "CHANGE", f"Self mood raised by {value}")
    
def lower_mood(value):
    alter_self_mood("h>n>s", value)
    log.data_collection("MOOD ENGINE", "CHANGE", f"Self mood lowered by {value}")
    
#---------------------------------------------- 1.user interaction
def self_alter_mood_user_interaction():
    try:
        current_user_interaction_tracker = mfl.flag_return("user_interaction_tracker")
        if current_user_interaction_tracker >= 2:
            raise_mood(0.1)
            mfl.flag_update("user_interaction_tracker", 0)
        elif current_user_interaction_tracker <= -2:
            lower_mood(0.1)
            mfl.flag_update("user_interaction_tracker", 0)
        else:
            return
    except Exception as e:
        log.data_collection("MOOD ENGINE", "ERROR", f"Error altering self mood based on user interaction: {e}")
#---------------------------------------------- 2.shutdown    
def self_alter_mood_failed_shutdown():
    lower_mood(0.5)

def self_alter_mood_successful_shutdown():
    raise_mood(0.2)
#---------------------------------------------- 3.Interpretation
def self_alter_mood_successful_interpretation():
    raise_mood(0.3)

def self_alter_mood_failed_interpretation():
    lower_mood(0.2)
#---------------------------------------------- 4.Learning
def self_alter_mood_new_words():
    raise_mood(0.1)
def self_alter_mood_new_intent():
    raise_mood(0.2)
#---------------------------------------------- 5.Silence
def self_alter_mood_silence():
    lower_mood(0.1)
def self_alter_mood_unsilence():
    raise_mood(0.1)
#---------------------------------------------- 6.Tell a Joke
def self_alter_mood_tell_joke():
    raise_mood(0.1)