from plugin import plugin
from Asset import backend
import termcolor2 as tc
from workspace_manager_module import workspace_manager


@plugin("move")
def move_to_other_branch_function():
    item_you_want_to_move = int(input(
        f"Enter {tc.colored('number', 'yellow')} you want to move: ")) - 1
    M_L = backend.view(workspace_manager.current_workspace)
    items = M_L[item_you_want_to_move]
    print(backend.list_tables())
    try:
        x_item = input(f"Enter new {tc.colored('branch', 'yellow')}: ")
        backend.move_data(
            workspace_manager.current_workspace, x_item, items[0])
    except:
        print("Please choose between your optoins")
