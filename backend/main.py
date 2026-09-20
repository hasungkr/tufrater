"""
Runs the main pipeline for TUFRater
"""

import pandas as pd

from scraper import fetch_all_levels, build_rated_levels, save_raw_levels
from parser import parse_all_gameplay_features, merge_and_save, load_raw_levels
from train import load_data, train, MODEL_PATH

def run_pipeline():
    print("=== Stage 1: Scraping level list ===")
    all_levels = fetch_all_levels()
    rated_levels = build_rated_levels(all_levels)
    save_raw_levels(rated_levels)   
    print(f"{len(rated_levels)} rated levels found.\n")

    print("=== Stage 2: Parsing gameplay features ===")
    df = load_raw_levels() 
    gameplay_features = parse_all_gameplay_features(df)
    merge_and_save(df, gameplay_features)
    print()

    print("=== Stage 3: Training model ===")
    dataset = load_data()
    trained_model = train(dataset)
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    trained_model.save_model(str(MODEL_PATH))
    print(f"Model saved to {MODEL_PATH}")

    return trained_model


if __name__ == "__main__":
    run_pipeline()