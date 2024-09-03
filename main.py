""" In the name of GOD """
import os
import sys
import importlib
import termcolor2
import pyfiglet
from Asset import backend
from Asset.plugins import exit_list
from plugin import plugins
from workspace_manager_module import workspace_manager


if os.name == 'nt':
    os.system('color')
print(termcolor2.colored(pyfiglet.figlet_format("IN THE NAME OF GOD"), 'red'))

if os.path.dirname(__file__) == '':
    PATH = '.' + os.path.sep
else:
    PATH = os.path.dirname(__file__)
    PATH = PATH + os.path.sep

ENCRYPTED_DATABASE = False
if os.path.isfile(PATH + f"Asset{os.sep}config.py"):
    from Asset import config  # pylint: disable = E0611,C0412

    ENCRYPTED_DATABASE = True
    if os.path.isfile(PATH + f"Asset{os.sep}list_of_work.db.gpg"):
        config.decrypt()

workspace_manager.switch_workspace('lof')


def import_plugins():
    """Import all plugins exist in Asset/plugins folder and get program access to them"""
    plugins = {}  # pylint: disable=W0621
    # the plugins directory path
    plugins_dir = "Asset.plugins"  # change to directory

    # make a list from all files inside the plugins directory
    for filename in os.listdir(f"{PATH}Asset{os.sep}plugins"):  # directory path
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]  # remove '.py' part from the name
            module = importlib.import_module(
                f'{plugins_dir}.{module_name}')  # استفاده از نام بسته
            plugins[module_name] = module
    return plugins


import_plugins()


M_L = []
backend.fill_list(backend.view(workspace_manager.current_workspace))
M_L = backend.view(workspace_manager.current_workspace)
print("---------------------------------------------")
print(M_L)
print("---------------------------------------------")
plugins["show"]()


while True:
    try:
        what_to_do = input("->:\n").lower()
    except KeyboardInterrupt:
        print("for exit the program please type 'exit'")
    int_check_var = False  # pylint: disable=invalid-name
    current_workspace = workspace_manager.get_workspace()  # Get the current workspace
    try:
        if isinstance(int(what_to_do), int):
            try:
                lNumber = int(what_to_do)
                if lNumber >= 0:
                    add_number = 1  # pylint: disable=invalid-name
                    li = M_L[lNumber - 1]
                    backend.update(li[0], title=li[1], value=(
                        int(li[2]) + add_number), constant=li[3], comment=li[4], workspace=workspace_manager.current_workspace)
                    # M_L[lNumber - 1][2] += 1
                elif lNumber < 0:
                    lNumber = abs(lNumber)
                    add_number = -1  # pylint: disable=invalid-name
                    li = M_L[lNumber - 1]
                    backend.update(li[0], title=li[1], value=(
                        int(li[2]) + add_number), constant=li[3], comment=li[4], workspace=workspace_manager.current_workspace)
                    # M_L[lNumber - 1][2] -= 1
                int_check_var = True  # pylint: disable=invalid-name
            except IndexError:
                print("Your input number is out of range")
    except NameError:
        pass
    except ValueError as e:
        # print(e)
        pass
    if int_check_var:
        pass
    elif "what_to_do" not in globals():
        continue
    elif what_to_do in exit_list:
        if ENCRYPTED_DATABASE:
            config.encrypt()
            os.remove(PATH + f"Asset{os.sep}list_of_work.db")
        elif not os.path.isfile(PATH + f"Asset{os.sep}list_of_work.db.gpg") and os.path.isfile(
                PATH + f"Asset{os.sep}config.py"):
            config.encrypt()
        sys.exit()
    # elif what_to_do == "show":
    #     new_show()
    elif what_to_do in plugins:
        try:
            plugins[what_to_do]()
        except KeyError:
            print("You are not entering the connrect information. Please try again!")
            # print(e)
        except KeyboardInterrupt:
            print("for exit the program please type 'exit'")
    else:
        print("Your command is not supported")
    M_L = []
    # Use the workspace variable from the manager
    try:
        backend.fill_list(backend.view(workspace_manager.current_workspace))
        M_L = backend.view(workspace_manager.current_workspace)
    except Exception:
        pass
    # try:
    #     print(M_L[lNumber - 1])
    # except NameError:
    #     pass
    # except IndexError:
    #     pass
