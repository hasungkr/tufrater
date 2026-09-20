"""
SQLite Database function connection for levels.db.
"""

import sqlite3
from pathlib import Path
 
DB_PATH = Path(__file__).resolve().parent / "data" / "levels.db"

def get_db():
    con = sqlite3.connect(DB_PATH, timeout=10)
    con.row_factory = sqlite3.Row
    return con