from plugin import plugin
from Asset import backend
import termcolor2
import json
from workspace_manager_module import workspace_manager


@plugin("show item")
def show_item():
    """Show full details of a single item or all items if 0 is entered"""
    workspace = workspace_manager.current_workspace
    M_L = backend.view(workspace)

    # Show simple list with indices for user to choose
    print(termcolor2.colored("Available items:", "yellow"))
    for idx, item in enumerate(M_L, start=1):
        print(f"{idx}) {item[1]}")

    # Ask user which one to show
    index = int(input(termcolor2.colored(
        "Enter the number of the item to view (0 for all): ", "green"
    )))

    def display_entry(item):
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

        print(termcolor2.colored(f"\nTitle: {title}", "cyan"))
        print(termcolor2.colored(f"Constant: {constant}", "magenta"))
        print(termcolor2.colored(f"Value:\n{display_value}", "green"))
        print(termcolor2.colored(f"Comment: {item[4]}", "yellow"))

    if index == 0:
        # Show all entries
        for item in M_L:
            display_entry(item)
    elif 1 <= index <= len(M_L):
        # Show only selected entry
        display_entry(M_L[index - 1])
    else:
        print(termcolor2.colored("Invalid number entered.", "red"))
