""" In the name of GOD """
import os
import sys
import importlib
import termcolor2
import pyfiglet
import readline  # <-- Added for autocomplete
import json
from Asset import backend
from Asset.plugins import exit_list
from plugin import plugins
from workspace_manager_module import workspace_manager
from vlc_track import VLCListerner

# --- Configs ---
vlc_tracker_start = True

# --- Constants and Path Setup ---
if os.name == 'nt':
    os.system('color')

print(termcolor2.colored(pyfiglet.figlet_format("IN THE NAME OF GOD"), 'red'))

PATH = os.path.dirname(__file__) + os.path.sep if os.path.dirname(__file__) else '.' + os.path.sep

ENCRYPTED_DATABASE = False
if os.path.isfile(PATH + f"Asset{os.sep}config.py"):
    from Asset import config  # pylint: disable = E0611,C0412
    ENCRYPTED_DATABASE = True
    if os.path.isfile(PATH + f"Asset{os.sep}list_of_work.db.gpg"):
        config.decrypt()

# --- Workspace Setup ---
workspace_manager.switch_workspace('lof')

# --- runing the vlc_tracker ---
if vlc_tracker_start and workspace_manager.current_workspace == 'lof':
    vlc_listener = VLCListerner()
    vlc_listener.start_in_background()

# --- Plugin Importer ---
def import_plugins():
    """Import all plugins from Asset/plugins folder and return as a dict."""
    plugins_dict = {}
    plugins_dir = "Asset.plugins"
    for filename in os.listdir(f"{PATH}Asset{os.sep}plugins"):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]
            module = importlib.import_module(f'{plugins_dir}.{module_name}')
            plugins_dict[module_name] = module
    return plugins_dict

# --- Load Plugins ---
all_plugins = import_plugins()

# --- Autocomplete Setup ---
def get_all_commands(plugins, all_plugins):
    commands = set()
    commands.update(plugins.keys())
    commands.update(all_plugins.keys())
    for cmd, val in plugins.items():
        if isinstance(val, dict):
            for sub in val.keys():
                commands.add(f"{cmd} {sub}")
    for cmd, val in all_plugins.items():
        if isinstance(val, dict):
            for sub in val.keys():
                commands.add(f"{cmd} {sub}")
    commands.update(exit_list)
    return sorted(commands)

def completer(text, state):
    options = [cmd for cmd in get_all_commands(plugins, all_plugins) if cmd.startswith(text)]
    if state < len(options):
        return options[state]
    return None

readline.parse_and_bind("tab: complete")
readline.set_completer(completer)

# --- Main List Initialization ---
def refresh_main_list():
    backend.fill_list(backend.view(workspace_manager.current_workspace))
    return backend.view(workspace_manager.current_workspace)

M_L = refresh_main_list()
print("---------------------------------------------")
print(M_L)
print("---------------------------------------------")
plugins["show"]()

# --- Command Handlers ---
def handle_number_command(lNumber, M_L):
    try:
        idx = abs(lNumber) - 1
        add_number = 1 if lNumber >= 0 else -1
        li = M_L[idx]
        value, constant = li[2], li[3]

        # Check if this is the new JSON format
        if constant == "episodes":
            try:
                ep_map = json.loads(value)
                last_season = str(max(int(s) for s in ep_map.keys()))
                last_episode = max(ep_map[last_season])

                new_episode = last_episode + add_number
                if new_episode < 1:
                    print("Episode cannot be less than 1")
                    return False

                # Append new episode instead of replacing the last one
                ep_map[last_season].append(new_episode)
                new_value = json.dumps(ep_map)

                backend.update(
                    li[0],
                    title=li[1],
                    value=new_value,
                    constant=constant,
                    comment=li[4],
                    workspace=workspace_manager.current_workspace
                )
            except Exception as e:
                print("Failed to update JSON episodes:", e)
                return False
        else:
            # Old integer format
            backend.update(
                li[0],
                title=li[1],
                value=int(value) + add_number,
                constant=constant,
                comment=li[4],
                workspace=workspace_manager.current_workspace
            )

        return True

    except IndexError:
        print("Your input number is out of range")
    except ValueError:
        print("Invalid input. Please enter a number.")
    return False

def handle_plugin_command(command, plugins):
    try:
        if command in plugins:
            plugins[command]()
            return True
        parts = command.split()
        main_command = parts[0]
        sub_command = parts[1] if len(parts) > 1 else None
        if main_command in plugins:
            plugin = plugins[main_command]
            if sub_command and hasattr(plugin, sub_command):
                getattr(plugin, sub_command)()
            elif sub_command and isinstance(plugin, dict) and sub_command in plugin:
                plugin[sub_command]()
            else:
                print(f"Invalid subcommand: {sub_command}")
            return True
    except Exception as e:
        print('Issue from running plugin command. Please report it to programmer.')
        print(e)
    return False

def handle_exit():
    if ENCRYPTED_DATABASE:
        config.encrypt()
        db_path = PATH + f"Asset{os.sep}list_of_work.db"
        if os.path.isfile(db_path):
            os.remove(db_path)
    elif not os.path.isfile(PATH + f"Asset{os.sep}list_of_work.db.gpg") and os.path.isfile(PATH + f"Asset{os.sep}config.py"):
        config.encrypt()
    sys.exit()

# --- Main Loop ---
while True:
    try:
        what_to_do = input("->:\n").lower()
    except KeyboardInterrupt:
        print("\nOK I will exit the program.")
        sys.exit()

    int_check_var = False
    show_status = True

    # Handle numeric commands
    if what_to_do.isdigit() or (what_to_do.startswith('-') and what_to_do[1:].isdigit()):
        lNumber = int(what_to_do)
        int_check_var = handle_number_command(lNumber, M_L)
    elif what_to_do == '':
        pass
    elif what_to_do in exit_list:
        handle_exit()
    elif handle_plugin_command(what_to_do, plugins):
        pass
    elif handle_plugin_command(what_to_do, all_plugins):
        pass
    else:
        print("Your command is not supported")

    # Refresh M_L with the current workspace data
    try:
        M_L = refresh_main_list()
    except Exception as e:
        print(f"An error occurred: {e}")

    # Show updated item if applicable
    try:
        if int_check_var and 'lNumber' in locals():
            print(M_L[abs(lNumber) - 1])
    except Exception:
        pass
