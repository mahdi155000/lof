#               IN THE NAME OF GOD
import os
import sqlite3
from workspace_manager_module import workspace_manager

if os.path.dirname(__file__) == '':
    PATH = '.' + os.path.sep
else:
    PATH = os.path.dirname(__file__)
    PATH = PATH + os.path.sep
current_workspace = workspace_manager.current_workspace


def connect(workspace=current_workspace):
    """Make a connection between database and program"""
    conn = sqlite3.connect(PATH + "list_of_work.db")
    cur = conn.cursor()
    cur.execute(
        f"""CREATE TABLE IF NOT EXISTS {workspace}(id INTEGER PRIMARY KEY, title 
        TEXT, value BLOB, constant text, comment TEXT)""")
    conn.commit()
    conn.close()


def switch_workspace(workspace_name):
    """change between database table."""
    connection = sqlite3.connect(PATH + 'list_of_work.db')
    global current_workspace
    current_workspace = None
    connect()
    connection.close()


def reanme_workspace(oldname, newname):
    """changeing the name of tables

    Args:
        oldname (text): old branch name
        newname (text): new name for branch
    """
    if oldname == 'lof':
        raise ValueError(
            "The 'lof' table cannot be renamed.\n if you want make you branch clear you have to do it manually")
    conn = sqlite3.connect(PATH + "list_of_work.db")
    cur = conn.cursor()
    cur.execute(
        f'ALTER TABLE {oldname} RENAME TO {newname}'
    )
    conn.commit()
    conn.close()


def list_tables():
    """
    Returns a list of all table names in the specified SQLite database.

    :param db_path: Path to the SQLite database file
    :return: List of table names
    """
    # Connect to the SQLite database
    conn = sqlite3.connect(PATH + "list_of_work.db")
    cur = conn.cursor()

    # Execute SQL command to get all table names
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")

    # Fetch all results
    tables = cur.fetchall()

    # Close the connection
    conn.close()

    # Convert results to a simple list of table names
    return [table[0] for table in tables]


def delete_workspace(workspace_name):
    """Remove a table from databae"""
    conn = sqlite3.connect(PATH + "list_of_work.db")
    cur = conn.cursor()
    cur.execute(f'DROP TABLE IF EXISTS {workspace_name}')
    conn.commit()
    conn.close()


def insert(titile='', value='', constant='', comment='', workspace=None):
    """Insert a new row on database"""
    conn = sqlite3.connect(PATH + "list_of_work.db")
    cur = conn.cursor()
    cur.execute(f"INSERT INTO {workspace} VALUES (NULL, ?, ?, ?, ?)",
                (titile, value, constant, comment))
    conn.commit()
    conn.close()


def view(workspace='lof'):
    """Will show database data"""
    conn = sqlite3.connect(PATH + "list_of_work.db")
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {workspace}")
    row = cur.fetchall()
    conn.close()
    return row


def search(title, value, comment, constant, workspace=None):
    """search between database data"""
    conn = sqlite3.connect(PATH + "list_of_work.db")
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {workspace} WHERE title=? OR value=? OR constant=? OR comment=?",
                (title, value, constant, comment))
    row = cur.fetchall()
    conn.close()
    return row


def delete(id, workspace=None):  # pylint: disable=redefined-builtin,invalid-name
    """remove a row from database"""
    conn = sqlite3.connect(PATH + "list_of_work.db")
    cur = conn.cursor()
    cur.execute(f"DELETE FROM {workspace} WHERE id=?", (id,))
    conn.commit()
    conn.close()


def update(id, title='',  # pylint: disable=redefined-builtin,too-many-arguments,invalid-name
           value='', constant='', comment='', workspace=None):
    """update a row information"""
    conn = sqlite3.connect(PATH + "list_of_work.db")
    cur = conn.cursor()
    cur.execute(f"UPDATE {workspace} SET  title=?, value=?, constant=?, comment=? WHERE id=?",
                (title, value, constant, comment, id))
    conn.commit()
    conn.close()


def update_id(last_id, new_id, workspace=None):
    """will update only the ID of row"""
    conn = sqlite3.connect(PATH + "list_of_work.db")
    cur = conn.cursor()
    cur.execute(f"UPDATE {workspace} SET id=? WHERE id=?", (new_id, last_id))
    conn.commit()
    conn.close()


def move_data(current_branch, newbranch, id):
    conn = sqlite3.connect(PATH + "list_of_work.db")
    cur = conn.cursor()
    cur.execute(
        f"""INSERT INTO {newbranch} (id, title, value, constant, comment)
SELECT id, title, value, constant, comment
FROM {current_branch}
WHERE id = ?""", (id,))
    cur.execute(f"DELETE FROM {current_branch} WHERE id = ?", (id,))
    conn.commit()
    conn.close()


M_L = []


def fill_list(loff):
    """Import all data from database into program"""
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
