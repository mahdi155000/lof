#               IN THE NAME OF GOD
import os
import sqlite3
import shutil

if os.path.dirname(__file__) == '':
    PATH = '.' + os.path.sep
else:
    PATH = os.path.dirname(__file__)
    PATH = PATH + os.path.sep

M_L = []
def fill_list(loff):
    for work in loff:
        M_L.insert(10000,work)

def connect():
    conn = sqlite3.connect(PATH + "list_of_work.db")
    cur = conn.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS lof (id INTEGER PRIMARY KEY, title TEXT, value BLOB, constant text, comment TEXT)")
    conn.commit()
    conn.close()


def insert(titile='', value='', constant='', comment=''):
    conn = sqlite3.connect(PATH + "list_of_work.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO lof VALUES (NULL, ?, ?, ?, ?)", (titile, value, constant, comment))
    conn.commit()
    conn.close()


def view():
    conn = sqlite3.connect(PATH + "list_of_work.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM lof")
    row = cur.fetchall()
    conn.close()
    return row


def search(title, value, comment, constant):
    conn = sqlite3.connect(PATH + "list_of_work.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM lof WHERE title=? OR value=? OR constant=? OR comment=?",
                (title, value, constant, comment))
    row = cur.fetchall()
    conn.close()
    return row


def delete(id):
    conn = sqlite3.connect(PATH + "list_of_work.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM lof WHERE id=?", (id,))
    conn.commit()
    conn.close()


def update(id, title='', value='', constant='', comment=''):
    conn = sqlite3.connect(PATH + "list_of_work.db")
    cur = conn.cursor()
    cur.execute("UPDATE lof SET  title=?, value=?, constant=?, comment=? WHERE id=?",
                (title, value, constant, comment, id))
    conn.commit()
    conn.close()


def update_id(last_id, new_id):
    conn = sqlite3.connect(PATH + "list_of_work.db")
    cur = conn.cursor()
    cur.execute("UPDATE lof SET id=? WHERE id=?", (new_id, last_id))
    conn.commit()
    conn.close()


connect()
# print(view())
# insert('Movies',1,'S04',"This is a movies")
# insert('Movies',0,"S04",'this is a movies')
# update(1,'halo', 3, 'S02','This is a film')
# update_id(4,3)
