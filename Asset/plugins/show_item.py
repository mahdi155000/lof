from plugin import plugin
from Asset import backend
import termcolor2

M_L = []
def fill_list(loff):
    for work in loff:
        M_L.insert(10000, work)
fill_list(backend.view())

        
@plugin("show-item")
def show_item_function():
    """for now it has to be change
    """
    for work in M_L:
        print(work) 