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


def encode_data(data: pd.DataFrame, enc_dict = None, window_size = 5):
    def encode(x, name):
        return x.map(enc_dict[name]).fillna(-1)

    if enc_dict is None:
        enc_dict = defaultdict(LabelEncoder)
        teams = list(set(TEAMS + data['hometeam'].values.tolist()))

        enc_dict['team'].fit(teams)
        enc_dict['referee'].fit(data['referee'])
        data['ftr'] = enc_dict['ftr'].fit_transform(data['ftr'])

        enc_dict = {name: dict(zip(le.classes_, le.transform(le.classes_))) for name, le in enc_dict.items()}
        pickle.dump(enc_dict, open(os.path.join(
            pathlib.Path(__file__).parent.resolve().parents[0], 'models/enc_dict'), 'wb'))
        
    data['referee'] = encode(data['referee'], 'referee')
    data['hometeam'] = encode(data['hometeam'], 'team')
    data['awayteam'] = encode(data['awayteam'], 'team')
    
    data[[f'ftr_{i}_home' for i in range(window_size, 0, -1)]] = (
        data[[f'ftr_{i}_home' for i in range(window_size, 0, -1)]]
        .apply(lambda x: encode(x, 'ftr'))
    )
    data[[f'ftr_{i}_away' for i in range(window_size, 0, -1)]] = (
        data[[f'ftr_{i}_away' for i in range(window_size, 0, -1)]]
        .apply(lambda x: encode(x, 'ftr'))
    )
    data = data.fillna(-1)
    return data

def retrieve_data():
    condition = """
    referee IS NOT NULL
    and bet_1x IS NOT NULL
    """
    data = retrieve(DB_COLUMNS, condition)
    return data

def prepare_dataset(stage = 'train', window_size = 5):
    def get_stats(row, home = True):
        team_loc = 'hometeam' if home else 'awayteam'
        
        res_arr = np.empty((len(columns), window_size), dtype = 'object')
        res_arr[:] = np.nan
        
        res = (
            data[
                (data['matchdate'] < row['matchdate'])
                 & ((data['hometeam'] == row[team_loc]) | (data['awayteam'] == row[team_loc]))
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
    data['matchdate'] = pd.to_datetime(data['matchdate'])
    data = data.sort_values('matchdate')
    data['bet_pred'] = data[['bet_1x', 'bet_x', 'bet_2x']].apply(lambda x: np.argmin(x.values), axis = 1)
    columns = [
            'ftr', 'fthg', 'ftag', 'hso', 'aso', 'hf',
            'af', 'hc', 'ac', 'hy', 'ay', 'hr', 'ar'
        ]
    new_columns = list(reduce(lambda x, y: x+y, 
                         [[f'{col}_{i}' for i in range(window_size, 0, -1)] for col in columns]))
    new_columns_home = list(map(lambda x: x+'_home', new_columns))
    new_columns_away = list(map(lambda x: x+'_away', new_columns))
            
    data[new_columns_home] = np.vstack(data.apply(get_stats, axis = 1, home = True).values)
    data[new_columns_away] = np.vstack(data.apply(get_stats, axis = 1, home = False).values)

    dates = data.pop('matchdate')
    hometeams = data['hometeam']
    awayteams = data['awayteam']
    #in order to update table
    output_keys = list(zip(dates, hometeams, awayteams))
    
    if stage == 'predict':
        data = data[data['played'] == 0]
        data = data.drop(columns = [
            'played', 'fthg', 'ftag', 'hso', 'aso', 'hf',
            'af', 'hc', 'ac', 'hy', 'ay', 'hr', 'ar', 'ftr'
            ])
    else:
        data = data[data['played'] == 1]
        data = data.drop(columns = [
            'played', 'fthg', 'ftag', 'hso', 'aso', 'hf',
            'af', 'hc', 'ac', 'hy', 'ay', 'hr', 'ar'
            ])
        data = data.dropna()
    return output_keys, data
