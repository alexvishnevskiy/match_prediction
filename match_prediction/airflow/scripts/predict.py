from match_prediction.airflow.scripts.prepare_data import prepare_dataset, encode_data, get_model_path
from match_prediction.airflow.scripts.db.ops import update
import pandas as pd
import numpy as np
import pickle
import joblib
import os


def load_model():
    model_path = get_model_path()
    model = joblib.load(model_path)
    return model

def predict(window_size = 5):
    enc_path = get_model_path(False)
    assert os.path.exists(enc_path), 'encoding dict should be trained'

    enc_dict = pickle.load(open(enc_path, 'rb'))
    init_data = prepare_dataset('predict', window_size)

    predict_data = init_data[init_data['status'] == 'SCHEDULED']
    predict_data = predict_data.drop(columns = [
            'winner', 'match_date', 'status', 'probs_1x', 'probs_x', 'probs_2x', 'fthg', 'ftag', 'hthg', 'htag'
        ])
    predict_data = encode_data(predict_data, enc_dict, window_size)
    model = load_model()
    probs = model.predict_proba(predict_data)
    probs = np.around(probs, 2)

    init_data.loc[predict_data.index, ['probs_1x', 'probs_x', 'probs_2x']] = probs
    init_data = init_data[init_data.columns[:13]]
    init_data = init_data.astype(object).where(pd.notnull(init_data),None)
    update(init_data)
    print("prediction's been done")

if __name__ == '__main__':
    predict()