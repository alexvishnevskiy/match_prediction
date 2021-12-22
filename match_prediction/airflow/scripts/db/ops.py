from configparser import ConfigParser
from typing import Union
import numpy as np
import time
import pandas as pd
import psycopg2


def config(filename='match_prediction/airflow/scripts/db/database.ini', section='postgresql'):
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

def create_temp_table(table_name: str = 'probs'):
    try:
        params = config()
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        cur = conn.cursor()

        create_statement = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            probs_1x float default null,
            probs_x float default null,
            probs_2x float default null
            );
        """
        
        cur.execute(create_statement) 
        conn.commit()
        cur.close()
        print(f"data's been inserted")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

#def insert_games(data: Union[list[dict], dict, list], table_name: str = 'games'):
def insert_games(data, table_name: str = 'games'):
    try:
        params = config()
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        if isinstance(data, dict):
            data = list(zip(*data.values()))
        elif isinstance(data[0], dict):
            data = list(map(lambda x: list(x.values()), data))

        args_str = ','.join(cur.mogrify(f"({', '.join(['%s']*len(x))})", x).decode("utf-8") for x in data)
        
        cur.execute(f"INSERT INTO {table_name} VALUES {args_str};") 
        conn.commit()
        cur.close()
        print(f"data's been inserted")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

#def update(data: Union[list[dict], pd.DataFrame]):
def update(data):
    try:
        params = config()
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        cur = conn.cursor()

        if isinstance(data, list):
            (
                winner, fthg, ftag, hthg, htag, hometeams,
                awayteams, status, date, referee
            ) = list(zip(*list(map(lambda x: x.values(), data))))
            date = tuple(map(lambda x: str(x), date))

            select_statement = """
            SELECT * FROM games
            WHERE home_team in %s
                AND away_team in %s
                AND match_date in %s
                AND referee in %s
            """
            cur.execute(select_statement, (hometeams, awayteams, date, referee))

            if len(cur.fetchall()):
                #I dont know why but it only works this way
                statement = """
                UPDATE games set status = c.status
                FROM (values %s
                ) as c(status)
                WHERE winner in %s
                    AND fthg in %s
                    AND ftag in %s
                    AND hthg in %s
                    AND htag in %s
                    AND home_team in %s
                    AND away_team in %s
                    AND match_date in %s
                    AND referee in %s
                """
                cur.execute(statement, (status, winner, fthg, ftag, hthg, htag, hometeams, awayteams, date, referee))
            else:
                insert_games(data)   

            conn.commit()
            cur.close() 
        else:
            cur.execute("TRUNCATE games")
            conn.commit()
            cur.close()

            insert_games(data.to_dict(orient = 'list'))
        print(f"data's been updated")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def retrieve(columns = None, condition: str = None):
    try:
        params = config()
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        cur = conn.cursor()
        if columns is not None:
            statement = f"SELECT {', '.join(columns)} FROM games"
        else:
            statement = "SELECT * FROM games"

        if condition:
            cur.execute(f"{statement} WHERE {condition}") 
        else:
            cur.execute(statement) 
        records = cur.fetchall()

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return records
