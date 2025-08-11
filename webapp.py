from flask import Flask, render_template, request, redirect, url_for, jsonify
from Asset import backend
from workspace_manager_module import workspace_manager
import requests
import sqlite3

app = Flask(__name__)

SERVER_URL = "http://192.168.1.185:5000"

def download_db():
    r = requests.get(SERVER_URL + "/api/download")
    items = r.json()
    # Save items to local SQLite
    conn = sqlite3.connect("list_of_work.db")
    cur = conn.cursor()
    for item in items:
        # Insert or update each item
        cur.execute("REPLACE INTO lof (id, title, value, constant, comment) VALUES (?, ?, ?, ?, ?)", item)
    conn.commit()
    conn.close()

def upload_db():
    conn = sqlite3.connect("list_of_work.db")
    cur = conn.cursor()
    cur.execute("SELECT id, title, value, constant, comment FROM lof")
    items = cur.fetchall()
    conn.close()
    r = requests.post(SERVER_URL + "/api/upload", json=items)
    print(r.json())

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        workspace = request.form.get('workspace')
        if workspace:
            workspace_manager.switch_workspace(workspace)
            backend.connect(workspace)
    ws = workspace_manager.current_workspace
    items = backend.view(ws)
    return render_template('index.html', items=items, workspace=ws)

@app.route('/add', methods=['POST'])
def add():
    text = request.form.get('text')
    ws = workspace_manager.current_workspace
    if text:
        backend.insert(titile=text, workspace=ws)
    return redirect(url_for('index'))

@app.route('/edit/<item_id>', methods=['POST'])
def edit(item_id):
    new_text = request.form.get('text')
    ws = workspace_manager.current_workspace
    if new_text:
        # Get current row to preserve other fields
        row = [r for r in backend.view(ws) if str(r[0]) == str(item_id)]
        if row:
            backend.update(int(item_id), title=new_text, value=row[0][2], constant=row[0][3], comment=row[0][4], workspace=ws)
    return redirect(url_for('index'))

@app.route('/delete/<item_id>', methods=['POST'])
def delete(item_id):
    ws = workspace_manager.current_workspace
    try:
        backend.delete(int(item_id), workspace=ws)
    except Exception as e:
        print("Delete error:", e)
    return redirect(url_for('index'))

@app.route('/plus/<item_id>', methods=['POST'])
def plus(item_id):
    ws = workspace_manager.current_workspace
    items = backend.view(ws)
    for item in items:
        if str(item[0]) == str(item_id):
            new_value = int(item[2]) + 1
            backend.edit_value(item_id, new_value, ws)
            break
    return redirect(url_for('index'))

@app.route('/edit_value/<item_id>', methods=['POST'])
def edit_value(item_id):
    ws = workspace_manager.current_workspace
    value = request.form.get('value')
    if value is not None:
        backend.edit_value(item_id, int(value), ws)
    return redirect(url_for('index'))

@app.route('/api/download', methods=['GET'])
def api_download():
    ws = workspace_manager.current_workspace
    items = backend.view(ws)
    return jsonify(items)

@app.route('/api/upload', methods=['POST'])
def api_upload():
    ws = workspace_manager.current_workspace
    data = request.get_json()
    # You must implement logic to merge/sync data
    # Example: overwrite local DB, or merge changes
    for item in data:
        backend.update_or_insert(item, workspace=ws)  # You must implement this
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(debug=True)