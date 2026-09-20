"""
Stage 1 of the main pipeline.
Scrapes all current levels from tuforums.com using their API and adds it to levels.db.
"""

import requests
import pandas as pd
import time
 
from core import TIER_VALUES
from db import get_db

def fetch_all_levels():
    all_levels = []
    page = 1

    while True:
        try:
            response = requests.get(
                "https://api.tuforums.com/v2/database/levels",
                params={"page": page, "limit": 500}, timeout=10
            )
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            break
        data = response.json()
        all_levels.extend(data["results"])

        print(f"Page {page} done | Total levels fetched so far: {len(all_levels)}")

        if not data["hasMore"]:
            break
        page += 1
        time.sleep(0.1)

    print(f"Pulled {len(all_levels)} levels total")
    return all_levels

def save_raw_levels(rated_levels):
    if not rated_levels:
        print("Error! rated_levels is empty, nothing saved.")
        return
 
    df = pd.DataFrame(rated_levels)
    schema_columns = [
        "id", "song", "creator", "difficulty", "difficulty_number", "tilecount",
        "levelLengthInMs", "bpm", "tuforums_link", "dlLink", "density",
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
                density REAL
            )
        """)
        df_to_save.to_sql("raw_levels", con, if_exists="replace", index=False)
 
    print(f"Database saved with {len(df_to_save)} levels (no gameplay features yet - run parser.py next).")

def build_rated_levels(all_levels):
    rated_levels = []

    for level in all_levels:
        diff = level.get("difficulty")
        level_id = level["id"]
        level["dlLink"] = f"https://api.tuforums.com/v2/database/levels/{level_id}/level.adofai"
        if isinstance(diff, dict):
            tier = diff.get("name")
            tier_upper = tier.upper() if tier else ""  # Removing Q Tiers
            # Skip junk tiers
            if tier and not tier_upper.startswith(("Q", "PQ", "GQ", "UQ")) and tier not in ["SPECIAL", "Censored", "Impossible", "Unranked"]:
                level["difficulty"] = tier
                level["tuforums_link"] = f"https://tuforums.com/levels/{level.get('id')}"

                ms = level.get("levelLengthInMs")
                if ms is None or float(ms) == 0:
                    print(f"Skipping level {level_id}: missing/invalid levelLengthInMs")
                    continue
                level["levelLengthInMs"] = round(float(ms) / 1000, 1)

                tile_count = level.get("tilecount")
                if tile_count is None or float(tile_count) == 0:
                    print(f"Skipping level {level_id}: missing/invalid tilecount")
                    continue
                tile_count_val = float(tile_count)

                level["density"] = ms / tile_count_val

                tier_letter = tier_upper[0]
                tier_number = tier[1:]

                if tier_letter in TIER_VALUES and tier_number.isdigit():
                    level["difficulty_number"] = TIER_VALUES[tier_letter] + int(tier_number)
                else:
                    print(f"Could not parse difficulty '{tier}' for level {level_id}, skipping")
                    continue

                rated_levels.append(level)

    return rated_levels


