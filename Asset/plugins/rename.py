from plugin import plugin
from Asset import backend
import termcolor2

M_L = []
def fill_list(loff):
    for work in loff:
        M_L.insert(10000, work)
fill_list(backend.view())

        
@plugin("rename")
def rename_function():
    item_you_want_to_rename = int(input(f"Enter {termcolor2.colored('name', 'yellow')} you want to rename: ")) - 1
    items = M_L[item_you_want_to_rename]
    x_item = input(f"Enter new {termcolor2.colored('name', 'yellow')}: ")
    backend.update(items[0], x_item, items[2], items[3], items[4])