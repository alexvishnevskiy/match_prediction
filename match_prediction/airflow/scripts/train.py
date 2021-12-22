from match_prediction.airflow.scripts.prepare_data import prepare_dataset, encode_data, get_model_path
from sklearn.ensemble import RandomForestClassifier
from match_prediction.airflow.scripts.db.scrapping import get_all_matches_stats
from match_prediction.airflow.scripts.db.ops import update
import joblib
import numpy as np


def fit():
    #data: list[dict] = get_all_matches_stats()
    data = get_all_matches_stats()
    data = list(filter(lambda x: x['referee'] is not None, data))
    update(data)

    data = prepare_dataset(stage = 'train')
    data = encode_data(data)
    y = data.pop('winner')
    X = data

    forest = RandomForestClassifier(n_estimators=300, max_depth=4, random_state=42)
    forest.fit(X, y)

    model_path = get_model_path()
    joblib.dump(forest, model_path)
    print("training's done")

if __name__ == '__main__':
    fit()