from plugin import plugin
from Asset import backend
import termcolor2


@plugin("rename")
def rename_function():
    item_you_want_to_rename = int(
        input(f"Enter {termcolor2.colored('name', 'yellow')} you want to rename: ")) - 1
    M_L = backend.view()
    items = M_L[item_you_want_to_rename]
    x_item = input(f"Enter new {termcolor2.colored('name', 'yellow')}: ")
    backend.update(items[0], x_item, items[2], items[3], items[4])
