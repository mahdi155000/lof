class WorkspaceManager:
    def __init__(self):
        self.current_workspace = 'default'

    def switch_workspace(self, new_workspace):
        self.current_workspace = new_workspace

    def get_workspace(self):
        return self.current_workspace


workspace_manager = WorkspaceManager()
