import sqlite3

path_to_db = 'bot_db'

def create_bdx():
    with sqlite3.connect(path_to_db) as db:
        # data about users apks
        try:
            db.execute("CREATE TABLE storage_tokens("
                       "token TEXT, rsa_pub TEXT, rsa_priv TEXT)")
            db.commit()
            print("DB was not found | Creating...")
        except Exception as e:
            print(e)

def add_token(token, rsa_pub, rsa_priv):
    with sqlite3.connect(path_to_db) as db:
        db.execute("INSERT INTO storage_tokens"
                   "(token, rsa_pub, rsa_priv)"
                   "VALUES (?, ?, ?)",
                   [token, rsa_pub, rsa_priv])
        db.commit()

def check_if_token_in_bd(token):
    with sqlite3.connect(path_to_db) as db:
        cur = db.cursor()
        cur.execute(f'SELECT * FROM storage_tokens WHERE token="{token}"')
        data = cur.fetchall()

        return len(data)

def get_special_token(token):
    with sqlite3.connect(path_to_db) as db:
        cur = db.cursor()
        cur.execute(f'SELECT * FROM storage_tokens WHERE token="{token}"')
        data = cur.fetchall()

        return data

def get_all():
    with sqlite3.connect(path_to_db) as db:
        cur = db.cursor()
        cur.execute(f'SELECT * FROM storage_tokens')
        data = cur.fetchall()

        return data
