from plugin import plugin
from Asset import backend
import termcolor2
import json
from workspace_manager_module import workspace_manager


@plugin("show item")
def show_item():
    """Show full details of each item, including full episode map if present"""
    M_L = backend.view(workspace_manager.current_workspace)
    for item in M_L:
        title = item[1]
        value = item[2]
        constant = item[3]

        if constant == "episodes":
            try:
                ep_map = json.loads(value)
                display_value = json.dumps(ep_map, indent=2)
            except Exception:
                display_value = value
        else:
            display_value = value

        text = f"{title:<30} | {display_value}"
        print(termcolor2.colored(text, 'cyan'))
