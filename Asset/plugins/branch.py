from plugin import register_command
from Asset import backend
from workspace_manager_module import workspace_manager as wk


@register_command('branch', 'add')
def add_function():
    get_name = input("Createing a new brnach: ")
    try:
        backend.connect(get_name)
        # print(backend.view(wk.current_workspace))
    except Exception as e:
        print("There was an error")
        print(e)


@register_command('branch', 'remove')
def remove_function():
    get_name = input("Enter you branch name to remove it: ")
    while True:
        try:
            backend.delete_workspace(get_name)
            break
        except KeyboardInterrupt:
            print("OK, nothing happend continue working")
        except:
            print("you branch does not exit please try again")
            break


# @register_command('branch', 'rename')
def rename():
    '''Change the name of a branch.'''
    pass


@register_command('branch' 'list')
def list_function():
    '''This function will make list of all brnaches exist  in database'''
    print("The list of branches is: ")
    for i in backend.list_tables():
        print(f'-> {i}\n')
