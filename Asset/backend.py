#               IN THE NAME OF GOD
import os
import sqlite3
import shutil

if os.path.dirname(__file__) == '':
    PATH = '.' + os.path.sep
else:
    PATH = os.path.dirname(__file__)
    PATH = PATH + os.path.sep
current_workspace = 'lof'


def connect(workspace='lof'):
    conn = sqlite3.connect(PATH + "list_of_work.db")
    cur = conn.cursor()
    cur.execute(
        f"CREATE TABLE IF NOT EXISTS {workspace}(id INTEGER PRIMARY KEY, title TEXT, value BLOB, constant text, comment TEXT)")
    conn.commit()
    conn.close()


def switch_workspace(workspace_name):
    connection = sqlite3.connect(PATH + 'list_of_work.db')
    cursor = connection.cursor()
    global current_workspace
    current_workspace = workspace_name
    connect()
    connection.close()


def delete_workspace(workspace_name):
    conn = sqlite3.connect(PATH + "list_of_work.db")
    cur = conn.cursor()
    cur.execute(f'DROP TABLE IF EXISTS {workspace_name}')
    conn.commit()
    conn.close()


def insert(titile='', value='', constant='', comment='', workspace='lof'):
    conn = sqlite3.connect(PATH + "list_of_work.db")
    cur = conn.cursor()
    cur.execute(f"INSERT INTO {workspace} VALUES (NULL, ?, ?, ?, ?)",
                (titile, value, constant, comment))
    conn.commit()
    conn.close()


def view(workspace="lof"):
    conn = sqlite3.connect(PATH + "list_of_work.db")
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {workspace}")
    row = cur.fetchall()
    conn.close()
    return row


def search(title, value, comment, constant, workspace='lof'):
    conn = sqlite3.connect(PATH + "list_of_work.db")
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {workspace} WHERE title=? OR value=? OR constant=? OR comment=?",
                (title, value, constant, comment))
    row = cur.fetchall()
    conn.close()
    return row


def delete(id, workspace='lof'):
    conn = sqlite3.connect(PATH + "list_of_work.db")
    cur = conn.cursor()
    cur.execute(f"DELETE FROM {workspace} WHERE id=?", (id,))
    conn.commit()
    conn.close()


def update(id, title='', value='', constant='', comment='', workspace='lof'):
    conn = sqlite3.connect(PATH + "list_of_work.db")
    cur = conn.cursor()
    cur.execute(f"UPDATE {workspace} SET  title=?, value=?, constant=?, comment=? WHERE id=?",
                (title, value, constant, comment, id))
    conn.commit()
    conn.close()


def update_id(last_id, new_id, workspace='lof'):
    conn = sqlite3.connect(PATH + "list_of_work.db")
    cur = conn.cursor()
    cur.execute(f"UPDATE {workspace} SET id=? WHERE id=?", (new_id, last_id))
    conn.commit()
    conn.close()


M_L = []


def fill_list(loff):
    for work in loff:
        M_L.insert(10000, work)


fill_list(view())
M_L = view()
connect()
# print(view())
# insert('Movies',1,'S04',"This is a movies")
# insert('Movies',0,"S04",'this is a movies')
# update(1,'halo', 3, 'S02','This is a film')
# update_id(4,3)
# connect("watched_movie")
# print(view("watched_movie"))
# insert('Movies',1,'S04',"This is a movies", 'watched_movie')
# print(view("watched_movie"))
