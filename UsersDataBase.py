import sqlite3


conn = sqlite3.connect("users_chatroom.db")
c = conn.cursor()


def create_table():
    try:
        c.execute("CREATE TABLE IF NOT EXISTS users(username TEXT, email TEXT, password TEXT)")
        conn.commit()
    except Exception as e:
        print("Błąd tworzenia tabeli", e)

#create_table()


def write_to_db(username, email, password):
    c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, password))
    conn.commit()


c.execute("SELECT * FROM users")
rows = c.fetchall()


def read_from_db():
    c.execute("SELECT * FROM users")
    rows = c.fetchall()

    for row in rows:
        print(row)

#write_to_db("user", "email", "pass")
read_from_db()


def delete():
    c.execute('DELETE FROM users', )
    conn.commit()

#delete()


def print_tables(con):

    cursorObj = con.cursor()

    cursorObj.execute('SELECT name from sqlite_master where type= "table"')

    print(cursorObj.fetchall())

#print_tables(conn)