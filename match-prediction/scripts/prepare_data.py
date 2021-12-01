from ..consts.db_vars import DB_COLUMNS, DATA_COLUMNS
from functools import reduce
from ..db.ops import retrieve
import numpy as np
import pandas as pd


def retrieve_data():
    condition = """
    referee IS NOT NULL
    and bet_1x IS NOT NULL
    """
    data = retrieve(condition)
    return data

def prepare_dataset(stage = 'train', window_size = 5):
    def get_stats(row, home = True):
        team_loc = 'HomeTeam' if home else 'AwayTeam'
        
        res_arr = np.empty((len(columns), window_size), dtype = 'object')
        res_arr[:] = np.nan
        
        res = (
            data[
                (data['Date'] < row['Date'])
                 & ((data['HomeTeam'] == row[team_loc]) | (data['AwayTeam'] == row[team_loc]))
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
    data['Date'] = pd.to_datetime(data['Date'])
    data = data.sort_values('Date')
    data['Bet_pred'] = data[['B365A', 'B365D', 'B365H']].apply(lambda x: np.argmin(x.values), axis = 1)
    columns = [
            'FTR', 'FTHG', 'FTAG', 'HS', 'AS', 'HF',
            'AF', 'HC', 'AC', 'HY', 'AY', 'HR', 'AR'
        ]
    new_columns = list(reduce(lambda x, y: x+y, 
                         [[f'{col}_{i}' for i in range(window_size, 0, -1)] for col in columns]))
    new_columns_home = list(map(lambda x: x+'_home', new_columns))
    new_columns_away = list(map(lambda x: x+'_away', new_columns))
            
    data[new_columns_home] = np.vstack(data.apply(get_stats, axis = 1, home = True).values)
    data[new_columns_away] = np.vstack(data.apply(get_stats, axis = 1, home = False).values)
    
    if stage == 'predict':
        data = data[data['played'] == 0]
    data = data.drop(columns = [
        'Date', 'played', 'FTHG', 'FTAG', 'HS', 'AS', 'HF',
        'AF', 'HC', 'AC', 'HY', 'AY', 'HR', 'AR', 'FTR'
    ])
    data = data.dropna()
    return data