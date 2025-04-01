import sqlite3

DB_NAME = 'arcade_users.db'

def create_table():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user TEXT PRIMARY KEY,
            roshambo INTEGER DEFAULT 0,
            tetris INTEGER DEFAULT 0,
            snake INTEGER DEFAULT 0,
            pacman INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def create_user_db(username):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    try:
        cur.execute('INSERT INTO users (user) VALUES (?)', (username,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()

def delete_user_db(username):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('DELETE FROM users WHERE user=?', (username,))
    conn.commit()
    conn.close()

def update_high_score(user, game, score):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(f'UPDATE users SET {game}=? WHERE user=?', (score, user))
    conn.commit()
    conn.close()

def get_high_score(user, game):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(f'SELECT {game} FROM users WHERE user=?', (user,))
    result = cur.fetchone()
    conn.close()
    return result[0] if result else 0

def get_all_users():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('SELECT user, roshambo, tetris, snake, pacman FROM users')
    users = cur.fetchall()
    conn.close()
    return users
