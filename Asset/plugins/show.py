from plugin import plugin
from Asset import backend
import termcolor2
import json
from workspace_manager_module import workspace_manager


@plugin("show")
@plugin("ls")
def show_function(do_what='plus'):
    M_L = backend.view(workspace_manager.current_workspace)
    id_counter = 1
    for item in M_L:
        title = item[1]
        value = item[2]
        constant = item[3]

        # Determine last episode number if it's a JSON map
        if constant == "episodes":
            try:
                ep_map = json.loads(value)
                # Get the last season and its highest episode
                last_season = max(int(s) for s in ep_map.keys())
                last_episode = max(ep_map[str(last_season)])
                display_value = last_episode  # Only the episode number
            except Exception:
                display_value = value
        else:
            display_value = value

        # Coloring
        show_color = 'blue' if item[0] % 2 else 'red'

        text = f"{id_counter}) for {do_what} one {title:<45} {display_value}"
        print(termcolor2.colored(text, show_color))
        id_counter += 1
