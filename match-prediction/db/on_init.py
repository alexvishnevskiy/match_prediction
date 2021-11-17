from .ops import insert_games
from .scrapping import get_all_matches_stats

def get_init_table(path):
   stats = get_all_matches_stats(path)
   insert_games(stats)