t#                       IN THE NAME OF GOD
import os
import sqlite3
import os
# from Asset import plugins
from Asset import backend
import termcolor2, pyfiglet
import importlib
from Asset.plugins import exit_list 
from plugin import plugins

            
    
if os.name == 'nt':
    os.system('color')
print(termcolor2.colored(pyfiglet.figlet_format("IN THE NAME OF GOD"), 'red'))

if os.path.dirname(__file__) == '':
    PATH = '.' + os.path.sep
else:
    PATH = os.path.dirname(__file__)
    PATH = PATH + os.path.sep

encrypted_database = False
if os.path.isfile(PATH + f"Asset{os.sep}config.py"):
    from Asset import config

    encrypted_database = True
    if os.path.isfile(PATH + f"Asset{os.sep}list_of_work.db.gpg"):
        config.decrypt()

def import_plugins():
    plugins = {}
    # the plugins directory path
    plugins_dir = "Asset.plugins"  # change to directory

    # make a list from all files inside the plugins directory
    for filename in os.listdir(f"{PATH}Asset{os.sep}plugins"):  # directory path
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]  # remove '.py' part from the name
            module = importlib.import_module(f'{plugins_dir}.{module_name}')  # استفاده از نام بسته
            plugins[module_name] = module 
    return plugins

def plus(item):
    M_L[item - 1][2] += 1


def fill_list(loff):
    for work in loff:
        M_L.insert(10000, work)


def new_show(do_what='plus'):
    id_counter = 1
    for item in M_L:
        if item[0] % 2:
            show_color = 'blue'
        else:
            show_color = 'red'
        if item[0] < 10:
            text = (" {:<1}) for {} one {:<45} {}".format(id_counter, do_what, item[1], item[2]))
        else:
            text = ("{:<1}) for {} one {:<45} {}".format(id_counter, do_what, item[1], item[2]))
        print(termcolor2.colored(text, show_color))
        id_counter += 1


# M_L = [[1, "test", 15], [2, "are you OK", 52]]

M_L = []

fill_list(backend.view())
print("---------------------------------------------")
print(M_L)
print("---------------------------------------------")
# print("{:<3}) {:<50} {:<10}".format('num', 'work', 'value'))
# print("Please enter your number:\n0) add\\minus\\set manually")
work_counter = 1
# for work in M_L:
#     print(f"{work_counter}) {work[1]}")
#     work_counter += 1
# show_item("plus")
new_show()
# print("enter 'c' for go to command mode.")

import_plugins()

while True:
    what_to_do = input("->:\n").lower()
    INT_check_var = False
    try:
        if type(int(what_to_do)) == int:
            try:
                lNumber = int(what_to_do)
                if lNumber >= 0:
                    addNumber = 1
                    li = M_L[lNumber - 1]
                    backend.update(li[0], title=li[1], value=int(li[2]) + addNumber, constant=li[3], comment=li[4])
                    # M_L[lNumber - 1][2] += 1
                elif lNumber < 0:
                    lNumber = abs(lNumber)
                    addNumber = -1
                    li = M_L[lNumber - 1]
                    backend.update(li[0], title=li[1], value=int(li[2]) + addNumber, constant=li[3], comment=li[4])
                    # M_L[lNumber - 1][2] -= 1
                INT_check_var = True
            except Exception as e:
                print("Your input number not in range")
    except Exception as e:
        # print(e)
        pass
    if INT_check_var:
        pass
    elif what_to_do in exit_list:
        if encrypted_database:
            # if os.path.isfile(PATH + f"Asset{os.sep}config.py"):
            config.encrypt()
            # os.remove('list_of_work.db', PATH + "Asset")
            os.remove(PATH + f"Asset{os.sep}list_of_work.db")
        elif not os.path.isfile(PATH + f"Asset{os.sep}list_of_work.db.gpg") and os.path.isfile(
                PATH + f"Asset{os.sep}config.py"):
            config.encrypt()
        exit(0)
    # elif what_to_do in plugins.plugins_list:
    # elif hasattr(plugins, what_to_do) and callable(getattr(plugins, what_to_do)):
    #     try:
    #         getattr(plugins, what_to_do)()
    #         M_L = []
    #         fill_list(backend.view())
    #     except Exception as e:
    #         pass
            # print("I can't run your command.")
            # print(e)

        # plugins.locals()
        # locals()[what_to_do]()
    elif what_to_do == "show":
        # show_item()
        new_show()
    elif what_to_do == "show item":
        from Asset import plugins

        plugins.show_item()
    elif what_to_do in plugins:
        plugins[what_to_do]()
    else:
        print("Your command is not supported")

    M_L = []
    fill_list(backend.view())
    try:
        # lNumber = int(what_to_do)
        print(M_L[lNumber - 1])
    except Exception as e:
        pass
        # print("Operating failed!!!")
        # print(e)
