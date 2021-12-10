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
#update 0->1
#model predictions
def update(data):
    try:
        params = config()
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        cur = conn.cursor()

        if len(data[0]) == 3:
            dates, hometeams, awayteams = zip(*data)
            statement = f"""
            UPDATE games set played = 1
                WHERE matchdate in {dates}
                AND hometeam in {hometeams}
                AND awayteam in {awayteams}
            """
        else:
            dates, hometeams, awayteams, probs = zip(*data)
            statement = f"""
            UPDATE games set
                probs_1x = c.probs_1x,
                probs_x = c.probs_x,
                probs_2x = c.probs_2x
            FROM (values {probs}
            ) as c(probs_1x, probs_x, probs_2x)
            WHERE matchdate in {dates}
                AND hometeam in {hometeams}
                AND awayteam in {awayteams}
            """

        cur.execute(statement) 
        conn.commit()
        cur.close()
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
