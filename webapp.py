from flask import Flask, render_template, request, redirect, url_for
from Asset import backend
from workspace_manager_module import workspace_manager

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True)