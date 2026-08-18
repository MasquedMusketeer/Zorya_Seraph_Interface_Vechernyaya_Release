from . import memory_flags_loader as mfl
from . import log_handler as log
import random
import math
import time

operator_mood_score = mfl.flag_return("operator_mood_score")
#__________________________________________________________________________________________________
#________________________________________MOOD HANDLER______________________________________________
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
            else:
                self_mood_score[mood_low] += value
                if self_mood_score[mood_low] > mood_max_value:
                    self_mood_score[mood_low] = mood_max_value
        
        elif self_mood_score[mood_low] > 2:
            self_mood_score[mood_low] = mood_max_value
            log.data_collection("MOOD ENGINE", "CHANGE", "Mood value over the allowed threshold, correction executed.")
        
        else:
            log.data_collection("MOOD ENGINE", "CHANGE", f"Request denied: current mood at max {mood_low} value.")
        
        self_mood_score[mood_high] = round(self_mood_score[mood_high], 1)
        self_mood_score[mood_med] = round(self_mood_score[mood_med], 1)
        self_mood_score[mood_low] = round(self_mood_score[mood_low], 1)
        mfl.flag_update("self_mood_score", self_mood_score)
    except Exception as e:
        log.data_collection("MOOD ENGINE", "ERROR", f"Error altering self mood: {e}")
        
        
def raise_mood(value, reason):
    log.data_collection("MOOD ENGINE", "CHANGE", f"Request: raise self mood by {value}. Reason: {reason}")
    alter_self_mood("s>n>h", value)
    
def lower_mood(value, reason):
    log.data_collection("MOOD ENGINE", "CHANGE", f"Request: lower self mood by {value}. Reason: {reason}")
    alter_self_mood("h>n>s", value)
#__________________________________________________________________________________________________
#_______________________________________MOOD TRIGGERS______________________________________________ 
#---------------------------------------------- 1.user interaction
def self_alter_mood_user_interaction():
    try:
        current_user_interaction_tracker = mfl.flag_return("user_interaction_tracker")
        if current_user_interaction_tracker >= 2:
            raise_mood(0.1, "User interacted substantially")
            mfl.flag_update("user_interaction_tracker", 0)
        elif current_user_interaction_tracker <= -2:
            lower_mood(0.1, "Left on the side for too long")
            mfl.flag_update("user_interaction_tracker", 0)
        else:
            return
    except Exception as e:
        log.data_collection("MOOD ENGINE", "ERROR", f"Error altering self mood based on user interaction: {e}")
#---------------------------------------------- 2.shutdown    
def self_alter_mood_failed_shutdown():
    lower_mood(0.5, "Shutdown error")
def self_alter_mood_successful_shutdown():
    raise_mood(0.1, "Sucessful Shutdown")
#---------------------------------------------- 3.Interpretation
def self_alter_mood_failed_interpretation():
    lower_mood(0.1, "Failed Interpretation")
#---------------------------------------------- 4.Learning
def self_alter_mood_new_words():
    raise_mood(0.1, "Learned a new word")
def self_alter_mood_new_intent():
    raise_mood(0.2, "Learned a new intent")
#---------------------------------------------- 5.Silence
def self_alter_mood_silence():
    lower_mood(0.1, "Got silenced")
def self_alter_mood_unsilence():
    raise_mood(0.1, "Got to speak again")
#---------------------------------------------- 6.Tell a Joke
def self_alter_mood_tell_joke():
    joke_count = mfl.flag_return("joke_count")
    if joke_count <3:
        raise_mood(0.1, "Told a Joke")
    else:
        log.data_collection("MOOD ENGINE", "CHANGE", "Request: raise self mood by 0.1" )
        log.data_collection("MOOD ENGINE", "CHANGE", "Request denied: joke saturation is over threshold.")
#---------------------------------------------- 7.Usefulness
def self_alter_mood_feeling_useful():
    usefulnes_score = mfl.flag_return("usefulness_score")
    if usefulnes_score < 4:
        usefulnes_score += 1
        mfl.flag_update("usefulness_score", usefulnes_score)
    if usefulnes_score >= 4:
        raise_mood(0.1, " Zorya is feeling useful")
        mfl.flag_update("usefulness_score", 0)
#__________________________________________________________________________________________________
#______________________________________MOOD AUDIO SCORE____________________________________________
def get_mood_compressed_score():
    try:
        current_score = mfl.flag_return("self_mood_score")
        mood_happy, mood_neutral, mood_sad = current_score["happy"], current_score["neutral"], current_score["sad"]
        mood_score_compressed = ((mood_happy *3/2) + mood_neutral + (mood_sad * 1/2))
        return mood_score_compressed
    except Exception as e:
        log.data_collection("MOOD ENGINE", "ERROR", f"Error calculating compressed mood score: {e}")

def get_stochastic_score_based_on_mood_compression(mood_comp_score: float):
    if mood_comp_score is None:
        return None
    else:
        try:
            low = math.floor(mood_comp_score)
            high = math.ceil(mood_comp_score)
            if low == high:
                return low
            prob_high = mood_comp_score - low 
            return high if random.random() < prob_high else low
        except Exception as e:
            log.data_collection("MOOD ENGINE", "ERROR", f"Error in stochastic score calculation: {e}")
#__________________________________________________________________________________________________
#______________________________________JOKE DEGRADATION____________________________________________
def degrade_joke_counter(stop_event):
    try:
        while not stop_event.is_set():
            joke_count = mfl.flag_return("joke_count")
            degradation_threshold = mfl.flag_return("joke_counter_degradation_threshold")
            if degradation_threshold > 0:
                degradation_threshold -= 1
                mfl.flag_update("joke_counter_degradation_threshold", degradation_threshold)
            elif degradation_threshold == 0:
                if joke_count > 0:
                    mfl.flag_update("joke_count", joke_count - 1)
                degradation_threshold = 3
            time.sleep(300)
    except Exception as e:
        log.data_collection("MEMORY", "ERROR", f"Error degrading joke counter: {e}")