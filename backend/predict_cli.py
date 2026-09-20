"""
Command line tool for manually testing the trained model using already rated TUF levels.
This is not part of the pipeline - this is for testing.

Note: The AI will likely give innacurate results for very high difficulty ranges, and levels
with high twirl_count and speed_change_count.

Run standalone:
    python predict_cli.py
"""

import requests
 
from core import load_model, predict_difficulty, extract_features_from_file

def run_ai_predictor(show_features=False):
    model = load_model("difficulty_model.txt")
    
    print("Paste in a TUF .adofai download link, or type 'quit' to exit. \n")
    while True:
        dl_link = input("Enter .adofai link: ").strip()

        if dl_link.lower() == "quit":
            print("Goodbye!")
            break
        try:
            response = requests.get(dl_link, timeout=10)
            response.raise_for_status()
            level_json = response.json()

            tier, raw_number = predict_difficulty(level_json, model)
            print(f"Predicted difficulty: {tier} (raw score: {raw_number:.2f})\n")

            if show_features:
                features = extract_features_from_file(level_json)
                print(features)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    run_ai_predictor()