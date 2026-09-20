"""
Stage 3 of the main pipeline.
Loads raw_levels from levels.db, then trains on the saved features to help improve prediction
accuracy. Saves the trained model to difficulty_model.txt. 
Run standalone:
    python train.py
"""

import lightgbm as lgb
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split 
from sklearn.metrics import mean_absolute_error, mean_squared_error

from db import get_db

num_round = 100
params = {
    "objective": "regression",
    "metric": "rmse",
    "verbosity": 1,
}

def load_data():
    with get_db() as con:
        df = pd.read_sql_query("SELECT * FROM raw_levels", con)
    return df

def train(df):
    X = df.drop(columns=["difficulty", "difficulty_number", "id", "song", "creator", "tuforums_link", "dlLink", "density", "levelLengthInMs"])
    y = df["difficulty_number"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    train_data = lgb.Dataset(X_train, label=y_train)
    test_data = lgb.Dataset(X_test, label=y_test, reference=train_data)

    model = lgb.train(params, train_data, num_boost_round=num_round, valid_sets=[test_data])

    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))

    print(f"MAE: {mae:.2f}")
    print(f"RMSE: {rmse:.2f}")

    importance = pd.Series(model.feature_importance(), index=X.columns).sort_values(ascending=False)
    model.save_model("difficulty_model.txt")
    print(importance)

    return model

if __name__ == "__main__":
    dataset = load_data()
    trained_model = train(dataset)
    trained_model.save_model("difficulty_model.txt")
    print("Model saved to difficulty_model.txt")