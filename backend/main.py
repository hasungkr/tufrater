"""
Runs the main pipeline for TUFRater
"""

import pandas as pd

from scraper import fetch_all_levels, build_rated_levels
from parser import parse_all_gameplay_features, merge_and_save
from train import load_data, train


def run_pipeline():
    print("=== Stage 1: Scraping level list ===")
    all_levels = fetch_all_levels()
    rated_levels = build_rated_levels(all_levels)
    df = pd.DataFrame(rated_levels)
    print(f"{len(df)} rated levels found.\n")

    print("=== Stage 2: Parsing gameplay features ===")
    gameplay_features = parse_all_gameplay_features(df)
    merge_and_save(df, gameplay_features)
    print()

    print("=== Stage 3: Training model ===")
    dataset = load_data()
    trained_model = train(dataset)
    trained_model.save_model("difficulty_model.txt")
    print("Model saved to difficulty_model.txt")

    return trained_model


if __name__ == "__main__":
    run_pipeline()