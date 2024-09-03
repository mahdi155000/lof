from plugin import plugin
from Asset import backend
import termcolor2
from workspace_manager_module import workspace_manager


@plugin("update")
def update_function():
    backend.fill_list(backend.view(workspace_manager.current_workspace))
    item_you_want_to_update = int(input(
        f"Enter {termcolor2.colored('number', 'yellow')} you want to update: ")) - 1
    M_L = backend.view(workspace_manager.current_workspace)
    items = M_L[item_you_want_to_update]
    updated_title = input("Enter new title: ")
    updated_value = input("Enter new value: ")
    updated_constant = input("Enter new constant: ")
    updated_comment = input("Enter new comment: ")
    if updated_title == '':
        updated_title = items[1]
        print(items[1])
    if updated_value == '':
        updated_value = items[2]
        print(items[2])
    if updated_constant == '':
        updated_constant = items[3]
        print(items[3])
    if updated_comment == '':
        updated_comment = items[4]
        print(items[4])
    backend.update(items[0], updated_title, updated_value,
                   updated_constant, updated_comment, workspace_manager.current_workspace)
