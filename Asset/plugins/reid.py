from plugin import plugin
from Asset import backend
import termcolor2
from workspace_manager_module import workspace_manager


@plugin("reid")
def reid_function():
    item_you_want_to_reid = int(
        input(f"Enter {termcolor2.colored('number', 'yellow')} you want to reid: ")) - 1
    M_L = backend.view(workspace_manager.current_workspace)
    items = M_L[item_you_want_to_reid]
    x_value = input(f"Enter new {termcolor2.colored('reid', 'yellow')}: ")
    backend.update_id(items[0], 0, workspace_manager.current_workspace)
    backend.update_id(x_value, items[0], workspace_manager.current_workspace)
    backend.update_id(0, x_value, workspace_manager.current_workspace)
