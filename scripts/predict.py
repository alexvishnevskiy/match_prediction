from sklearn import linear_model
import numpy as np
import pandas as pd
import joblib


def predict(X, model_path):
    if isinstance(X, list):
        X = np.array(X)
    assert X.shape[1] == 13, 'number of features should be 13'

    regressor = joblib.load(model_path)
    output = regressor.predict(X)
    return output