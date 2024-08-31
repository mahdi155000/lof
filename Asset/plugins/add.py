from plugin import plugin, register_help
from Asset import backend
import termcolor2

M_L = []
# This is for now I'll we fix this repeat lately
def fill_list(loff):
    for work in loff:
        M_L.insert(10000, work)

        
@register_help
@plugin("add")
def add_function():
    """This function will add a new title into program database"""
    fill_list(backend.view())
    M_L = backend.view()
    add_title = input("Enter Title: ")
    add_value = input("Input Value: ")
    try:
        if type(int(add_value)) is int:
            add_value = int(add_value)
    except:
        pass
    add_constant = input("Enter constant: ")
    add_comment = input("If you want, enter comment: ")
    backend.insert(add_title, add_value, add_constant, add_comment)