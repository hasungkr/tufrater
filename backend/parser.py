"""
Stage 2 of the main pipeline.
Parses .adofai files, extracting twirl count, and speed_change_count, merges them into raw_levels,
and saves the results back into levels.db.
"""

import pandas as pd
import requests

from concurrent.futures import ThreadPoolExecutor

from core import extract_gameplay_features
from db import get_db

MAX_WORKERS = 20

def load_raw_levels():
    with get_db() as con:
        return pd.read_sql_query("SELECT * FROM raw_levels", con)

def parse_one_level(row):

    try:
        resp = requests.get(row["dlLink"], timeout=10)
        level_json = resp.json()

        if "error" in level_json:
            print(f"Skipping id {row['id']}: {level_json['error']}")
            return None

        features = extract_gameplay_features(level_json)
        features["id"] = row["id"]
        return features
    except Exception as e:
        print(f"Error: Failed on id {row['id']} ({e})")
        return None

def parse_all_gameplay_features(df):
    rows = df.to_dict("records")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = list(executor.map(parse_one_level, rows))

    gameplay_features = []

    for r in results:
        if r is not None:
            gameplay_features.append(r)
    print(f"Successfully gained features for {len(gameplay_features)} levels.")
    return gameplay_features

def merge_and_save(df, gameplay_features):
    gameplay_df = pd.DataFrame(gameplay_features)
    df = df.merge(gameplay_df, on="id", how="left")
 
    # Drops rows where parsing failed (missing file, timeout, etc.)
    df = df.dropna(subset=["twirl_count", "speed_change_count"]).reset_index(drop=True)
 
    schema_columns = [
        "id", "song", "creator", "difficulty", "difficulty_number", "tilecount",
        "levelLengthInMs", "bpm", "tuforums_link", "dlLink", "density",
        "twirl_count", "speed_change_count",
    ]
    df_to_save = df.reindex(columns=schema_columns)
 
    with get_db() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS raw_levels (
                id INTEGER PRIMARY KEY,
                song TEXT,
                creator TEXT,
                difficulty TEXT,
                difficulty_number REAL,
                tilecount INTEGER,
                levelLengthInMs INTEGER,
                bpm REAL,
                tuforums_link TEXT,
                dlLink TEXT,
                density REAL,
                twirl_count INTEGER,
                speed_change_count INTEGER
            )
        """)
        df_to_save.to_sql("raw_levels", con, if_exists="replace", index=False)
 
    print(f"Database saved with gameplay features. {len(df_to_save)} levels total.")
 
 
if __name__ == "__main__":
    raw_df = load_raw_levels()
    features = parse_all_gameplay_features(raw_df)
    merge_and_save(raw_df, features)