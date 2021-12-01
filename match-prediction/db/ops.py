import os
import psycopg2
from configparser import ConfigParser


def config(filename='database.ini', section='postgresql'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db

def insert_games(data):
    try:
        params = config()
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        cur = conn.cursor()
        args_str = ','.join(cur.mogrify(f"({', '.join(['%s']*len(x))})", list(x.values())).decode("utf-8") for x in data)
        
        cur.execute(f"INSERT INTO games VALUES {args_str};") 
        conn.commit()
        cur.close()
        print(f"data's been inserted")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

#to be done
#update played: 0->1
def update():
    pass

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
