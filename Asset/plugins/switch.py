from plugin import plugin
from Asset import backend
from workspace_manager_module import workspace_manager


@plugin(f'switch')
def switch_branches():
    """This function will change the current workspace with another"""
    show_status = False
    print("Pleast select one of these workspaces: ")
    for table in backend.list_tables():
        print(f"-> {table}")
    # new_workspace = input("->: ")
    # backend.switch_workspace(new_workspace)
    # workspace_manager.set_workspace(new_workspace)
    # print(backend.view(new_workspace))
    # backend.fill_list(backend.view(new_workspace))
    # M_L = backend.view(new_workspace)
    try:
        workspace = input("    ->: ")
        workspace_manager.switch_workspace(workspace)
        backend.switch_workspace(workspace_manager.current_workspace)
        print(backend.view(workspace_manager.current_workspace))
        backend.fill_list(backend.view(workspace_manager.current_workspace))
        M_L = backend.view(workspace_manager.current_workspace)
    except Exception:
        print("please choose between your options")
