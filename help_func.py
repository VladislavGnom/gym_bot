import sqlite3 

con = sqlite3.connect(database="sqlite.db")

cursor = con.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS users
                (id INTEGER PRIMARY KEY AUTOINCREMENT,  
                full_name TEXT, 
                age INTEGER,
                gym TEXT,
                user_id INTEGER UNIQUE)
            """)


def register_user(data):
    try:
        param = (data['full_name'], data['age'], data['gym'], data['user_id'])
        cursor.execute("INSERT INTO users (full_name, age, gym, user_id) VALUES (?, ?, ?, ?)", param)
        con.commit()
        return True
    except sqlite3.IntegrityError as error:
        return False
