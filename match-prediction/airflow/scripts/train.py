from .prepare_data import prepare_dataset, encode_data
from sklearn.ensemble import RandomForestClassifier
from .db.ops import update
import pandas as pd
import numpy as np
import pathlib
import joblib
import os


def fit():
    output_keys, data = prepare_dataset(stage = 'train')
    data = encode_data(data)
    y = data.pop('ftr')
    X = data

    forest = RandomForestClassifier(n_estimators=300, max_depth=4, random_state=42)
    forest.fit(X, y)

    model_path = 'match-prediction/models/forest.joblib'
    joblib.dump(forest, model_path)
    update(output_keys)
    print("training's done")
