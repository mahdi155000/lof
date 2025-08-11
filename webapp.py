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
        backend.add(text, ws)
    return redirect(url_for('index'))

@app.route('/edit/<item_id>', methods=['POST'])
def edit(item_id):
    new_text = request.form.get('text')
    ws = workspace_manager.current_workspace
    if new_text:
        backend.edit(item_id, new_text, ws)
    return redirect(url_for('index'))

@app.route('/delete/<item_id>', methods=['POST'])
def delete(item_id):
    backend.delete(item_id)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)