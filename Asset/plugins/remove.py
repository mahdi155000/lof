from plugin import plugin
from Asset import backend
import termcolor2
from workspace_manager_module import workspace_manager


@plugin("remove")
def remove_function():
    print("runing remove function")
    M_L = backend.view(workspace_manager.current_workspace)
    item_you_want_to_delete = int(input(
        f"Enter {termcolor2.colored('number', 'yellow')} you want to delete: ")) - 1
    items = M_L[item_you_want_to_delete]
    backend.delete(items[0], workspace_manager.current_workspace)
    print("finish running")
