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

        self.items = self.load_items()
        self.filtered_items = self.items.copy()

        self.create_widgets()

    def create_widgets(self):
        search_frame = ttk.Frame(self)
        search_frame.pack(pady=10)
        tk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<KeyRelease>", self.update_list)

        container = ttk.Frame(self)
        container.pack(pady=10, fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.list_frame = ttk.Frame(canvas)

        self.list_frame.bind(
            "<Configure>", lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        frame_window = canvas.create_window((0, 0), window=self.list_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.update_list()

    def load_items(self):
        return {f"Item {i}": 0 for i in range(1, 21)}

    def update_list(self, event=None):
        search_term = self.search_entry.get().lower()
        self.filtered_items = {k: v for k, v in self.items.items() if search_term in k.lower()}

        for widget in self.list_frame.winfo_children():
            widget.destroy()

        for item, value in self.filtered_items.items():
            row_frame = ttk.Frame(self.list_frame)
            row_frame.pack(fill=tk.X, padx=5, pady=2)

            tk.Label(row_frame, text=f"{item}: {value}").pack(side=tk.LEFT, expand=True)
            ttk.Button(row_frame, text="Increment", command=lambda i=item: self.increment_item(i)).pack(side=tk.RIGHT)

    def increment_item(self, item):
        self.items[item] += 1
        self.update_list()

if __name__ == "__main__":
    app = Application()
    app.mainloop()
