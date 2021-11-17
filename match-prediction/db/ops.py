import psycopg2
from config import config


def insert_games(data):
    try:
        params = config()
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        cur = conn.cursor()
        args_str = ','.join(cur.mogrify(f"({', '.join(['%s']*len(x))})", list(x.values())).decode("utf-8") for x in data)
        
        cur.execute("INSERT INTO games VALUES " + args_str) 
        conn.commit()
        cur.close()
        print(f"{len(data)} rows've been inserted")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def retrieve(condition: str = None):
    try:
        params = config()
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        cur = conn.cursor()
        if condition:
            cur.execute(f"SELECT * FROM games WHERE {condition}") 
        else:
            cur.execute("SELECT * FROM games") 
        records = cur.fetchall()

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return records
