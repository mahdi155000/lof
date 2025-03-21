import sys
import importlib
import tkinter as tk
from tkinter import ttk
from plugin import plugins
import os 
from workspace_manager_module import workspace_manager
from Asset import backend

if os.path.dirname(__file__) == '':
    PATH = '.' + os.path.sep
else:
    PATH = os.path.dirname(__file__)
    PATH = PATH + os.path.sep

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
                f'{plugins_dir}.{module_name}')  # use module name
            plugins[module_name] = module
    return plugins

import_plugins()

M_L = []
backend.fill_list(backend.view(workspace_manager.current_workspace))
M_L = backend.view(workspace_manager.current_workspace)


root = tk.Tk()

root.title("lof project")
# root.geometry('600x400+50+50')
window_width = 600
window_height = 400

# get the screen dimension
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# find the center point
center_x = int(screen_width/2 - window_width / 2)
center_y = int(screen_height/2 - window_height / 2)

# set the position of the window to the center of the screen
root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

# test new lable and new lable
tk.Label(root, text="classic theme").pack()
ttk.Label(root, text="new theme").pack()





root.mainloop()