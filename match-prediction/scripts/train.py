from sklearn.preprocessing import LabelEncoder
from collections import defaultdict
import pandas as pd


def encode_data(data: pd.DataFrame, enc_dict = None, window_size = 5):
    if enc_dict is None:
        enc_dict = defaultdict(LabelEncoder)
        data['HomeTeam'] = enc_dict['team'].fit_transform(data['HomeTeam'])
        data['Referee'] = enc_dict['Referee'].fit_transform(data['Referee'])
        data['FTR'] = enc_dict['FTR'].fit_transform(data['FTR'])
    else:
        data['HomeTeam'] = enc_dict['team'].transform(data['HomeTeam'])
        data['Referee'] = enc_dict['Referee'].transform(data['Referee'])
        data['FTR'] = enc_dict['FTR'].transform(data['FTR'])

    data['AwayTeam'] = enc_dict['team'].transform(data['AwayTeam'])
    
    data[[f'FTR_{i}_home' for i in range(window_size, 0, -1)]] = (
        data[[f'FTR_{i}_home' for i in range(window_size, 0, -1)]]
        .apply(lambda x: enc_dict['FTR'].transform(x))
    )
    data[[f'FTR_{i}_away' for i in range(window_size, 0, -1)]] = (
        data[[f'FTR_{i}_away' for i in range(window_size, 0, -1)]]
        .apply(lambda x: enc_dict['FTR'].transform(x))
    )
    return data, enc_dict