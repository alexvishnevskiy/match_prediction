from .prepare_data import prepare_dataset, encode_data
from .db.ops import update
import pickle
import pandas as pd
import numpy as np
import pathlib
import joblib
import os


def load_model():
    model_path = 'match-prediction/models/forest.joblib'
    model = joblib.load(model_path)
    return model

def predict(window_size = 5):
    enc_path = 'match-prediction/models/enc_dict'
    assert os.path.exists(enc_path), 'encoding dict should be trained'

    enc_dict = pickle.load(open(enc_path, 'rb'))
    output_keys, data = prepare_dataset('predict', window_size)
    data = encode_data(data, enc_dict, window_size)
    model = load_model()
    probs = model.predict_proba(data)
    probs = list(zip(output_keys, probs))
    update(probs)
    print("prediction's been done")
