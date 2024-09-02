from plugin import plugin
from Asset import backend
import termcolor2

        
@plugin("show item")
def show_item():
    """for now it has to be change
    """
    M_L = backend.view()
    for work in M_L:
        print(work) 