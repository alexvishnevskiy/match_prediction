from .consts.db_vars import DB_COLUMNS, DATA_COLUMNS, TEAMS
from sklearn.preprocessing import LabelEncoder
from collections import defaultdict
from functools import reduce
from .db.ops import retrieve
import numpy as np
import pandas as pd
import pathlib
import pickle
import os


def get_model_path(model = True):
    model_sub_path = 'models/forest.joblib' if model else 'models/enc_dict'
    model_path = os.path.join(
        pathlib.Path(__file__).parent.resolve().parents[0], model_sub_path)
    return model_path

def encode_data(data: pd.DataFrame, enc_dict = None, window_size = 5):
    def encode(x, name):
        return x.map(enc_dict[name]).fillna(-1)

    if enc_dict is None:
        enc_dict = defaultdict(LabelEncoder)
        #teams = list(set(TEAMS + data['home_team'].values.tolist()))
        teams = data['home_team'].values.tolist()


        enc_dict['team'].fit(teams)
        enc_dict['referee'].fit(data['referee'])
        data['winner'] = enc_dict['winner'].fit_transform(data['winner'])

        enc_dict = {name: dict(zip(le.classes_, le.transform(le.classes_))) for name, le in enc_dict.items()}
        pickle.dump(enc_dict, open(get_model_path(False), 'wb'))
        
    data['referee'] = encode(data['referee'], 'referee')
    data['home_team'] = encode(data['home_team'], 'team')
    data['away_team'] = encode(data['away_team'], 'team')
    
    data[[f'winner_{i}_home' for i in range(window_size, 0, -1)]] = (
        data[[f'winner_{i}_home' for i in range(window_size, 0, -1)]]
        .apply(lambda x: encode(x, 'winner'))
    )
    data[[f'winner_{i}_away' for i in range(window_size, 0, -1)]] = (
        data[[f'winner_{i}_away' for i in range(window_size, 0, -1)]]
        .apply(lambda x: encode(x, 'winner'))
    )
    data = data.fillna(-1)
    return data

def retrieve_data():
    condition = "referee IS NOT NULL"
    data = retrieve(condition = condition)
    return data

def prepare_dataset(stage = 'train', window_size = 5):
    def get_stats(row, home = True):
        team_loc = 'home_team' if home else 'away_team'
        
        res_arr = np.empty((len(columns), window_size), dtype = 'object')
        res_arr[:] = np.nan
        
        res = (
            data[
                (data['match_date'] < row['match_date'])
                 & ((data['home_team'] == row[team_loc]) | (data['away_team'] == row[team_loc]))
            ]
            .iloc[-window_size:]
            [columns]
            .values
            .transpose()
        )
        
        if res.shape[1]:
            res_arr[:, :res.shape[1]] = res
        return res_arr.ravel()

    data: list = retrieve_data()
    data = pd.DataFrame(data, columns=DB_COLUMNS)
    data['match_date'] = pd.to_datetime(data['match_date'])
    data = data.sort_values('match_date')

    columns = ['winner', 'fthg', 'ftag', 'hthg', 'htag']
    new_columns = list(reduce(lambda x, y: x+y, 
                         [[f'{col}_{i}' for i in range(window_size, 0, -1)] for col in columns]))
    new_columns_home = list(map(lambda x: x+'_home', new_columns))
    new_columns_away = list(map(lambda x: x+'_away', new_columns))
            
    data[new_columns_home] = np.vstack(data.apply(get_stats, axis = 1, home = True).values)
    data[new_columns_away] = np.vstack(data.apply(get_stats, axis = 1, home = False).values)
    
    if stage != 'predict':
        data = data[data['status'] == 'FINISHED']
        data = data.drop(columns = [
            'status', 'match_date', 'probs_1x', 'probs_x', 'probs_2x', 'fthg', 'ftag', 'hthg', 'htag'
        ])
        data = data.dropna(subset = ['fthg_4_home', 'fthg_4_away'])
    return data