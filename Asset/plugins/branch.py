from Asset import backend
from workspace_manager_module import workspace_manager as wk


def add():
    get_name = input("Createing a new brnach: ")
    try:
        backend.connect(get_name)
        print(backend.view(wk.current_workspace))
    except Exception as e:
        print("There was an error")
        print(e)


def remove():
    pass


def rename():
    pass
