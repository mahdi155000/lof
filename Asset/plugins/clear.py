from plugin import plugin
import os


@plugin("clear")
def clear_function():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")
