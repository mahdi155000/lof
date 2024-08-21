from plugin import plugin
from Asset import backend
import termcolor2

M_L = []
# This is for now I'll we fix this repeat lately
def fill_list(loff):
    for work in loff:
        M_L.insert(10000, work)

@plugin("remove")
def remove_function():
    print("runing remove function")
    fill_list(backend.view())
    M_L = backend.view()
    item_you_want_to_delete = int(input(f"Enter {termcolor2.colored('number', 'yellow')} you want to delete: ")) - 1
    items = M_L[item_you_want_to_delete]
    backend.delete(items[0])
    print("finish running")