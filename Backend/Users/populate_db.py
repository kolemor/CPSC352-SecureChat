import sqlite3
import os

from users_hash import hash_password

database = "Backend/users.db"

#Remove database if it exists before creating and populating it
if os.path.exists(database):
    os.remove(database)

""" create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print("Error:", e)

    return conn

""" create a table from the create_table_sql statement
:param conn: Connection object
:param create_table_sql: a CREATE TABLE statement
:return:
"""
def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except sqlite3.Error as e:
        print("Error:", e)

# populates db
def populate_database():
    conn = create_connection(database)
    if conn == None:
        return 1

    user_table = """ CREATE TABLE IF NOT EXISTS user (
                            uid INTEGER PRIMARY KEY,
                            name TEXT NOT NULL UNIQUE,
                            password TEXT NOT NULL
                        ); """
    create_table(conn, user_table)

    status_table = """ CREATE TABLE IF NOT EXISTS status (
                            sid integer PRIMARY KEY,
                            status TEXT UNIQUE
                        ); """
    create_table(conn, status_table)

    userstatus_table = """ CREATE TABLE IF NOT EXISTS user_status (
                            user_id INTEGER,
                            status_id INTEGER,
                            PRIMARY KEY (user_id, status_id),
                            FOREIGN KEY (user_id) REFERENCES user (uid),
                            FOREIGN KEY (status_id) REFERENCES status (sid)
                        ); """
    create_table(conn, userstatus_table)

    cursor = conn.cursor()

    statuses = ['online', 'offline']
    
    for status in statuses:
        cursor.execute(
            """
            INSERT INTO status (status)
            VALUES (?)
            """,
            (status,)
        )
    
    cursor.execute(
        """
        INSERT INTO user (name, password)
        VALUES (?, ?)
        """,
        ("Test", hash_password("Test"))
    )

    cursor.execute(
        """
        INSERT INTO user_status (user_id, status_id)
        VALUES (?, ?)
        """,
        (1,2)
    )

    conn.commit()
    cursor.close()
    conn.close()

    print("Database populated :D")

if __name__ == "__main__":
    populate_database()