from prepare_data import prepare_dataset
import pandas as pd
import numpy as np
import pathlib
import joblib
import os


def load_model():
    model_path = os.path.join(
        pathlib.Path(__file__).parent.resolve().parents[0], 'models/forest.joblib')
    model = joblib.load(model_path)
    return model

def predict(window_size = 5):
    data = prepare_dataset('predict', window_size)
    model = load_model()
    probs = model.predict_proba(data)
    return probs

print(predict())