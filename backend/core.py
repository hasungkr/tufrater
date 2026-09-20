"""
Core logic for the TUFRater predictions. Contains all the functions needed.
Import what you need here. E.g.
    from core.py import load_model, predict_difficulty
"""

import pandas as pd
import lightgbm as lgb

TIER_VALUES = {"P": 0, "G": 20, "U": 40}

# .adofai feature extraction

def extract_gameplay_features(level_json):
    actions = level_json.get("actions", [])
 
    twirl_count = 0
    speed_change_count = 0
 
    for action in actions:
        event_type = action.get("eventType")
        if event_type == "Twirl":
            twirl_count += 1
        elif event_type == "SetSpeed":
            speed_change_count += 1
 
    return {
        "twirl_count": twirl_count,
        "speed_change_count": speed_change_count,
    }

# Prediction process

def num_to_pgu(number):
    rounded = round(number)
    clamped = max(1, min(rounded, 60))

    if clamped <= 20:
        letter = "P"
        tier_number = clamped
    elif clamped <= 40:
        letter = "G"
        tier_number = clamped - 20
    elif clamped <= 60:
        letter = "U"
        tier_number = clamped - 40
    return f"{letter}{tier_number}"

def extract_features_from_file(level_json):
    settings = level_json.get("settings", {})
    angle_data = level_json.get("angleData", [])
    actions = level_json.get("actions", [])

    tile_count = len(angle_data)
    bpm = settings.get("bpm", 0)

    twirl_count = 0
    speed_change_count = 0

    for action in actions:
        event_type = action.get("eventType")
        if event_type == "Twirl":
            twirl_count += 1
        elif event_type == "SetSpeed":
            speed_change_count += 1

    return {
        "tilecount": tile_count,
        "bpm": bpm,
        "twirl_count": twirl_count,
        "speed_change_count": speed_change_count,
    }
    
def predict_difficulty(level_json, model):
    features = extract_features_from_file(level_json)
    X_input = pd.DataFrame([features])
    predicted_number = model.predict(X_input)[0]
    return num_to_pgu(predicted_number), predicted_number

# Model usage

def load_model(path="difficulty_model.txt"):
    return lgb.Booster(model_file=path)