from ops import insert_games
from scrapping import get_all_matches_stats

def get_init_table():
   stats = get_all_matches_stats()
   insert_games(stats)

#parse args
if __name__ == '__main__':
   get_init_table()