#               IN THE NAME OF GOD
import os
import sqlite3
from workspace_manager_module import workspace_manager
import json
from datetime import datetime

# --- Paths ---
if os.path.dirname(__file__) == '':
    PATH = '.' + os.path.sep
else:
    PATH = os.path.dirname(__file__) + os.path.sep

current_workspace = workspace_manager.current_workspace

# --- Database connection and table creation ---
def connect(workspace=current_workspace):
    """Make a connection between database and program"""
    conn = sqlite3.connect(PATH + "list_of_work.db")
    cur = conn.cursor()
    cur.execute(
        f"""CREATE TABLE IF NOT EXISTS {workspace}(
            id INTEGER PRIMARY KEY,
            title TEXT,
            value BLOB,
            constant TEXT,
            comment TEXT,
            sessions TEXT
        )"""
    )
    conn.commit()
    conn.close()

# --- Workspace management ---
def switch_workspace(workspace_name):
    """Change between database table."""
    global current_workspace
    current_workspace = workspace_name
    connect(workspace_name)

def rename_workspace(oldname, newname):
    """Rename table in the database."""
    if oldname == 'lof':
        raise ValueError(
            "The 'lof' table cannot be renamed.\nIf you want to make a branch clear, do it manually."
        )
    conn = sqlite3.connect(PATH + "list_of_work.db")
    cur = conn.cursor()
    cur.execute(f'ALTER TABLE {oldname} RENAME TO {newname}')
    conn.commit()
    conn.close()

def list_tables():
    """Return all table names in the database."""
    conn = sqlite3.connect(PATH + "list_of_work.db")
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [table[0] for table in cur.fetchall()]
    conn.close()
    return tables

def delete_workspace(workspace_name):
    """Remove a table from database"""
    conn = sqlite3.connect(PATH + "list_of_work.db")
    cur = conn.cursor()
    cur.execute(f'DROP TABLE IF EXISTS {workspace_name}')
    conn.commit()
    conn.close()

# --- CRUD operations ---
def insert(titile='', value='', constant='', comment='', workspace=None, sessions=None):
    """Insert a new row on database"""
    if sessions is None:
        sessions = json.dumps([])
    conn = sqlite3.connect(PATH + "list_of_work.db")
    cur = conn.cursor()
    cur.execute(
        f"INSERT INTO {workspace} VALUES (NULL, ?, ?, ?, ?, ?)",
        (titile, value, constant, comment, sessions)
    )
    conn.commit()
    conn.close()

def view(workspace='lof'):
    """Return all rows of the workspace"""
    conn = sqlite3.connect(PATH + "list_of_work.db")
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {workspace}")
    row = cur.fetchall()
    conn.close()
    return row

def search(title, value, comment, constant, workspace=None):
    """Search between database data"""
    conn = sqlite3.connect(PATH + "list_of_work.db")
    cur = conn.cursor()
    cur.execute(
        f"SELECT * FROM {workspace} WHERE title LIKE ? OR value=? OR constant=? OR comment LIKE ?",
        (f"%{title}%", value, constant, f"%{comment}%")
    )
    row = cur.fetchall()
    conn.close()
    return row

def delete(id, workspace=None):
    """Remove a row from database"""
    conn = sqlite3.connect(PATH + "list_of_work.db")
    cur = conn.cursor()
    cur.execute(f"DELETE FROM {workspace} WHERE id=?", (id,))
    conn.commit()
    conn.close()

def update(id, title='', value='', constant='', comment='', workspace=None, sessions=None):
    """Update a row information"""
    conn = sqlite3.connect(PATH + "list_of_work.db")
    cur = conn.cursor()
    # If sessions is None, don't overwrite
    if sessions is None:
        cur.execute(
            f"UPDATE {workspace} SET title=?, value=?, constant=?, comment=? WHERE id=?",
            (title, value, constant, comment, id)
        )
    else:
        cur.execute(
            f"UPDATE {workspace} SET title=?, value=?, constant=?, comment=?, sessions=? WHERE id=?",
            (title, value, constant, comment, json.dumps(sessions), id)
        )
    conn.commit()
    conn.close()

def update_id(last_id, new_id, workspace=None):
    """Update only the ID of a row"""
    conn = sqlite3.connect(PATH + "list_of_work.db")
    cur = conn.cursor()
    cur.execute(f"UPDATE {workspace} SET id=? WHERE id=?", (new_id, last_id))
    conn.commit()
    conn.close()

def move_data(current_branch, newbranch, id):
    conn = sqlite3.connect(PATH + "list_of_work.db")
    cur = conn.cursor()
    cur.execute(
        f"""INSERT INTO {newbranch} (title, value, constant, comment, sessions)
           SELECT title, value, constant, comment, sessions
           FROM {current_branch} WHERE id=?""", (id,))
    cur.execute(f"DELETE FROM {current_branch} WHERE id=?", (id,))
    conn.commit()
    conn.close()

# --- Program memory ---
M_L = []

def fill_list(loff):
    """Import all data from database into program"""
    global M_L
    M_L = []
    for work in loff:
        M_L.append(work)
    return M_L

# Initialize M_L
fill_list(view(current_workspace))
connect()

# --- Edit helpers ---
def edit_value(id, value, workspace):
    """Update only the value field of a row"""
    conn = sqlite3.connect(PATH + "list_of_work.db")
    cur = conn.cursor()
    cur.execute(f"UPDATE {workspace} SET value=? WHERE id=?", (value, id))
    conn.commit()
    conn.close()

# --- VLC session tracking feature ---
def add_session(id, start_time, end_time, workspace=None):
    """Add a session for a given row id with start and end timestamps"""
    workspace = workspace or current_workspace
    conn = sqlite3.connect(PATH + "list_of_work.db")
    cur = conn.cursor()
    cur.execute(f"SELECT sessions FROM {workspace} WHERE id=?", (id,))
    row = cur.fetchone()
    if row:
        sessions = json.loads(row[0]) if row[0] else []
        sessions.append({
            "start": start_time.isoformat(),
            "end": end_time.isoformat(),
            "duration_seconds": int((end_time - start_time).total_seconds())
        })
        cur.execute(f"UPDATE {workspace} SET sessions=? WHERE id=?", (json.dumps(sessions), id))
    conn.commit()
    conn.close()

def add_sessions_column(workspace):
    conn = sqlite3.connect(PATH + "list_of_work.db")
    cur = conn.cursor()
    cur.execute(f"ALTER TABLE {workspace} ADD COLUMN sessions TEXT")
    conn.commit()
    conn.close()

# ----------------------------
# New functions for JSON episodes + sessions
# ----------------------------

def insert_json_episode(titile='', value='', constant='', comment='', sessions=None, workspace=None):
    """Insert a new row with JSON episodes and session info"""
    conn = sqlite3.connect(PATH + "list_of_work.db")
    cur = conn.cursor()
    cur.execute(
        f"INSERT INTO {workspace} VALUES (NULL, ?, ?, ?, ?, ?)",
        (titile, value, constant, comment, json.dumps(sessions or []))
    )
    conn.commit()
    conn.close()


def update_json_episode(id, title='', value='', constant='', comment='', sessions=None, workspace=None):
    """Update a row with JSON episodes and session info"""
    conn = sqlite3.connect(PATH + "list_of_work.db")
    cur = conn.cursor()
    cur.execute(
        f"UPDATE {workspace} SET title=?, value=?, constant=?, comment=?, sessions=? WHERE id=?",
        (title, value, constant, comment, json.dumps(sessions or []), id)
    )
    conn.commit()
    conn.close()

def update_database():
    conn = sqlite3.connect(PATH + "list_of_work.db")
    cur = conn.cursor()
    cur.execute(
        f"ALTER TABLE lof ADD COLUMN sessions TEXT DEFAULT ''"
    )
    conn.commit()
    conn.close()

def view_with_sessions(workspace='lof'):
    """
    View database rows including the new 'sessions' column.
    Returns a list of tuples: (id, title, value, constant, comment, sessions)
    """
    conn = sqlite3.connect(PATH + "list_of_work.db")
    cur = conn.cursor()
    
    # Try to fetch the sessions column; if it does not exist, return None for sessions
    try:
        cur.execute(f"SELECT id, title, value, constant, comment, sessions FROM {workspace}")
        rows = cur.fetchall()
    except sqlite3.OperationalError:
        # Fallback if 'sessions' column doesn't exist
        cur.execute(f"SELECT id, title, value, constant, comment FROM {workspace}")
        rows = [(r + (None,)) for r in cur.fetchall()]

    conn.close()
    return rows

def update_sessions(id, new_session, workspace=None):
    """
    Append a new session to the `sessions` column of the row.
    `new_session` is a dict like: {"start": timestamp, "end": timestamp, "duration": seconds}
    """
    workspace = workspace or current_workspace
    conn = sqlite3.connect(PATH + "list_of_work.db")
    cur = conn.cursor()
    # Get existing sessions
    cur.execute(f"SELECT sessions FROM {workspace} WHERE id=?", (id,))
    row = cur.fetchone()
    if row is None:
        conn.close()
        return
    existing = row[0]
    try:
        sessions = json.loads(existing) if existing else []
    except Exception:
        sessions = []
    sessions.append(new_session)
    cur.execute(f"UPDATE {workspace} SET sessions=? WHERE id=?", (json.dumps(sessions), id))
    conn.commit()
    conn.close()
