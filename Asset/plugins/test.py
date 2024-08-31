import os
import importlib
from plugin import plugins,plugin

if os.path.dirname(__file__) == '':
    PATH = '.' + os.path.sep
else:
    PATH = os.path.dirname(__file__)
    PATH = PATH + os.path.sep
def import_plugins():
    plugins = {}
    # the plugins directory path
    plugins_dir = "Asset.plugins"  # change to directory

    # make a list from all files inside the plugins directory
    for filename in os.listdir(f"{PATH}"):  # directory path
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]  # remove '.py' part from the name
            module = importlib.import_module(f'{plugins_dir}.{module_name}')  # استفاده از نام بسته
            plugins[module_name] = module 
    return plugins

import_plugins()


@plugin("test")
def test_function():
    print(plugins)