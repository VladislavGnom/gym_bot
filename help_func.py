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


cursor.execute("""CREATE TABLE IF NOT EXISTS gym_sport_table
                (id INTEGER PRIMARY KEY AUTOINCREMENT,  
                name_trainer TEXT,
                call_data TEXT)
            """)


cursor.execute("""CREATE TABLE IF NOT EXISTS workout
                (id INTEGER PRIMARY KEY AUTOINCREMENT,  
                 max_weight INTEGER,
                 count_repeat INTEGER,
                 user_id INTEGER,
                 trainer_id INTEGER,
                 date DATE,
                 FOREIGN KEY (user_id)  REFERENCES users (id)
                 FOREIGN KEY (trainer_id)  REFERENCES gym_sport_table (id) )
            """)


def exist_user(user_id):
    data = cursor.execute("SELECT id FROM users WHERE user_id=?", (user_id, ))
    if data:
        return True
    else:
        return False


def register_user(data):
    try:
        param = (data['full_name'], data['age'], data['gym'], data['user_id'])
        cursor.execute("INSERT INTO users (full_name, age, gym, user_id) VALUES (?, ?, ?, ?)", param)
        con.commit()
        return True
    except sqlite3.IntegrityError as error:
        return False
    

def get_user(message):
    user_id = message.from_user.id
    data = cursor.execute("SELECT full_name, age, gym FROM users WHERE user_id=?", (user_id, ))
    return data.fetchone()


def get_trainers(message):
    data = get_user(message)
    if data[2] == "Gym Sport":
        all_trainers = cursor.execute("SELECT name_trainer, call_data FROM gym_sport_table")
        return all_trainers.fetchall()
    

def get_trainer_id(call_data):
    data = cursor.execute("SELECT id FROM gym_sport_table WHERE call_data=?", (call_data, ))
    return data.fetchone()[0]


def get_user_id(user_id):
    data = cursor.execute("SELECT id FROM users WHERE user_id=?", (user_id, ))
    return data.fetchone()[0]


def get_current_data():
    from datetime import date
    current_date = date.today()
    return current_date


def get_trainer(trainer_id):
    data = cursor.execute(f"SELECT name_trainer FROM gym_sport_table WHERE id = {trainer_id}")
    return data.fetchone()[0]



def save_result(data):
    try:
        param = (data['max_weight'], data['count_repeat'], get_current_data(), get_user_id(data['user_id']), get_trainer_id(data['call_data']))
        cursor.execute("INSERT INTO workout (max_weight, count_repeat, date, user_id, trainer_id) VALUES (?, ?, ?, ?, ?)", param)
        con.commit()
        return True
    except Exception as error:
        print(error)
        return False


def get_data_trainers(user_id, date):
    print(get_user_id(user_id))
    data = cursor.execute(f"SELECT max_weight, count_repeat, trainer_id FROM workout WHERE date = '{date}' AND user_id = {get_user_id(user_id)}")
    return data.fetchall()


def output_data_trainers(user_id, date):
    text = ""
    data = get_data_trainers(user_id, date)
    for d in data:
        text += (f"<b>{get_trainer(d[2])}:</b>\n\n<b>Максимально поднятый вес:</b> {d[0]}кг \n<b>Количество повторений:</b> {d[1]} \n\n----------------------------\n")

    return text