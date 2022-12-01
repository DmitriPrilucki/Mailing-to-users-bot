import sqlite3


db = sqlite3.connect('dima_mail_1.db')
cur = db.cursor()


async def db_conn():
    cur.execute("CREATE TABLE IF NOT EXISTS users_count (user_id INTEGER PRIMARY KEY, count INT DEFAULT 0, desc TEXT DEFAULT 'NO', time INT DEFAULT 0)")
    db.commit()


async def new_user(user_id):
    cur.execute("INSERT INTO users_count (user_id) VALUES(?)", (user_id,))
    db.commit()


async def all_user():
    all_people = cur.execute("SELECT user_id FROM users_count WHERE count = 0").fetchall()
    return all_people


async def update_count(count):
    cur.execute(f"UPDATE users_count SET count = {count}").fetchall()
    db.commit()