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


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Item Manager")
        self.geometry("400x300")

        # Dictionary to hold items and their values
        self.items = self.load_items()
        self.filtered_items = self.items.copy()

        self.create_widgets()

    def create_widgets(self):
        # Search section
        search_frame = ttk.Frame(self)
        search_frame.pack(pady=10)
        tk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<KeyRelease>", self.update_list)

        # Items list
        self.tree = ttk.Treeview(self, columns=("value", "action"), show="headings")
        self.tree.heading("value", text="Value")
        self.tree.heading("action", text="Action")
        self.tree.pack(pady=10, fill=tk.BOTH, expand=True)

        self.update_list()

    def load_items(self):
        # This function should be modified to load items from your project's data source
        # For demonstration, we'll use a static dictionary
        return {"Item 1": 0, "Item 2": 0, "Item 3": 0, "Item 4": 0}

    def update_list(self, event=None):
        search_term = self.search_entry.get().lower()
        self.filtered_items = {k: v for k, v in self.items.items() if search_term in k.lower()}

        # Clear current items in the list
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Add filtered items to the list
        for item, value in self.filtered_items.items():
            self.tree.insert("", tk.END, values=(item, value, "Increment"), tags=(item,))
            self.tree.tag_bind(item, "<Double-1>", lambda event, item=item: self.increment_item(item))

    def increment_item(self, item):
        self.items[item] += 1
        self.update_list()

if __name__ == "__main__":
    app = Application()
    app.mainloop()