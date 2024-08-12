import sqlite3 

con = sqlite3.connect(database="sqlite.db")

cursor = con.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS users
                (id INTEGER PRIMARY KEY AUTOINCREMENT,  
                full_name TEXT, 
                age INTEGER,
                gym TEXT)
            """)


def register_user(data):
    param = (data['full_name'], data['age'], data['gym'])
    cursor.execute("INSERT INTO users (full_name, age, gym) VALUES (?, ?, ?)", param)
    con.commit()

