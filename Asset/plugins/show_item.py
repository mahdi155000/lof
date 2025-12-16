from plugin import plugin
from Asset import backend
import termcolor2
import json
from workspace_manager_module import workspace_manager
import time

# --- Add this import to get VLC status ---
from vlc_track import VLCListerner

# Create a tracker instance to query status on demand
vlc_tracker = VLCListerner()

@plugin("show item")
def show_item():
    """Show full details of a single item or all items if 0 is entered"""
    workspace = workspace_manager.current_workspace
    M_L = backend.view_with_sessions(workspace)  # Use the new view that includes sessions

    print(termcolor2.colored("Available items:", "yellow"))
    for idx, item in enumerate(M_L, start=1):
        print(f"{idx}) {item[1]}")

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

        # Episodes value handling
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

        # --- Show old sessions format or new JSON sessions ---
        if sessions:
            try:
                sessions_list = json.loads(sessions)
            except Exception:
                sessions_list = None

            # If sessions_list is valid and not empty
            if sessions_list:
                last = sessions_list[-1]
                start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(last.get('start', 0)))
                end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(last.get('end', 0)))
                duration = last.get('duration')

                # Show old/new session durations
                print(termcolor2.colored(
                    f"Last played: start={start_time}, end={end_time}, duration={duration}s", "red"))
        else:
            # If old database format stored sessions differently
            if isinstance(item, tuple) and len(item) > 5 and item[5] is not None:
                try:
                    print(termcolor2.colored(f"Last played (old format): {item[5]}", "red"))
                except Exception:
                    pass

        # --- Add VLC on-demand duration info if available ---
        # Only check when printing a specific item (not for every command)
        try:
            status = vlc_tracker.get_status()
            if status:
                print(termcolor2.colored("\nVLC Current Status:", "blue"))
                print(f"Status: {status['status']}")
                print(f"Position: {status['position']:.2f}s")
                if status['duration'] is not None:
                    print(f"Duration: {status['duration']:.2f}s")
                else:
                    print("Duration: unknown (not provided by VLC)")
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
