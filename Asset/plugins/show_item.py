from plugin import plugin
from Asset import backend
import termcolor2
import json
from workspace_manager_module import workspace_manager
import time


@plugin("show item")
def show_item():
    """Show full details of a single item or all items if 0 is entered"""
    workspace = workspace_manager.current_workspace
    M_L = backend.view_with_sessions(workspace)  # Use the new view that includes sessions

    # Show simple list with indices for user to choose
    print(termcolor2.colored("Available items:", "yellow"))
    for idx, item in enumerate(M_L, start=1):
        print(f"{idx}) {item[1]}")

    # Ask user which one to show
    try:
        index = int(input(termcolor2.colored(
            "Enter the number of the item to view (0 for all): ", "green"
        )))
    except ValueError:
        print(termcolor2.colored("Invalid input. Please enter a number.", "red"))
        return

    def display_entry(item):
        title = item[1]
        value = item[2]
        constant = item[3]
        comment = item[4]
        sessions = item[5] if len(item) > 5 else None

        # Display episodes
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
        print(termcolor2.colored(f"Comment: {comment}", "yellow"))

        # Display latest session
        if sessions:
            try:
                sessions_list = json.loads(sessions)
                if sessions_list:
                    last = sessions_list[-1]
                    start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(last['start']))
                    end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(last['end']))
                    duration = last['duration']
                    print(termcolor2.colored(
                        f"Last played: start={start_time}, end={end_time}, duration={duration}s", "red"))
            except Exception:
                pass

    # Show all or selected entry
    if index == 0:
        for item in M_L:
            display_entry(item)
    elif 1 <= index <= len(M_L):
        display_entry(M_L[index - 1])
    else:
        print(termcolor2.colored("Invalid number entered.", "red"))
