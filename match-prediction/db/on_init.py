import ops
import scrapping

if __name__ == '__main__':
   path = 'https://www.xscores.com/soccer/england/premier-league'
   stats = scrapping.get_all_matches_stats(path)
   ops.insert_games(stats)