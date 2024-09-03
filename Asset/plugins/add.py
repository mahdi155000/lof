from plugin import plugin, register_help
from Asset import backend
import termcolor2
from workspace_manager_module import workspace_manager


@register_help
@plugin("add")
def add_function():
    """This function will add a new title into program database"""
    M_L = backend.view(workspace_manager.current_workspace)
    add_title = input("Enter Title: ")
    add_value = input("Input Value: ")
    try:
        if type(int(add_value)) is int:
            add_value = int(add_value)
    except:
        pass
    add_constant = input("Enter constant: ")
    add_comment = input("If you want, enter comment: ")
    backend.insert(add_title, add_value, add_constant,
                   add_comment, workspace_manager.current_workspace)
