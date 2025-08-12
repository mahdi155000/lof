from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
from Asset import backend
from workspace_manager_module import workspace_manager
import requests

app = Flask(__name__)

SERVER_URL = "http://192.168.1.100:5000"  # Change to your server's IP

def download_db():
    r = requests.get(SERVER_URL + "/api/download_db")
    with open("list_of_work.db", "wb") as f:
        f.write(r.content)
    print("Database downloaded.")

def upload_db():
    with open("list_of_work.db", "rb") as f:
        files = {'dbfile': f}
        r = requests.post(SERVER_URL + "/api/upload_db", files=files)
    print("Database uploaded:", r.json())

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

@app.route('/api/download_db', methods=['GET'])
def download_db_api():
    # Send the database file to the client
    return send_file('Asset/list_of_work.db', as_attachment=True)

@app.route('/api/upload_db', methods=['POST'])
def upload_db_api():
    # Receive the database file from the client and overwrite the server's copy
    file = request.files['dbfile']
    file.save('Asset/list_of_work.db')
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)