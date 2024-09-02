from plugin import plugin
from Asset import backend


@plugin(f'switch')
def switch_branches():
    """This function will change the current workspace with another"""
    print("Pleast select one of these workspaces: ")
    for table in backend.list_tables():
        print(f"-> {table}")
    workspace = input("->: ")
    backend.switch_workspace(workspace)
    print(backend.view(workspace))
    backend.fill_list(backend.view(workspace))
    M_L = backend.view(workspace)
