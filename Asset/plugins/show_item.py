from plugin import plugin
from Asset import backend
import termcolor2
from workspace_manager_module import workspace_manager


@plugin("show item")
def show_item():
    """for now it has to be change
    """
    M_L = backend.view(workspace_manager.current_workspace)
    for work in M_L:
        print(work)
