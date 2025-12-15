from plugin import plugin
from Asset import backend
import json
import termcolor2
from workspace_manager_module import workspace_manager


@plugin("convert_episodes")
def convert_episodes():
    workspace = workspace_manager.current_workspace
    rows = backend.view(workspace)

    backend.fill_list(rows)

    index = int(input(
        f"Enter {termcolor2.colored('number', 'yellow')} to convert: "
    )) - 1

    row = rows[index]
    row_id, title, value, constant, comment = row

    try:
        season = int(constant)
        episode = int(value)
    except ValueError:
        print(termcolor2.colored(
            "This entry is not in old season/episode format.", "red"
        ))
        return

    print(f"\nConverting: {termcolor2.colored(title, 'cyan')}")
    print(f"Detected → Season {season}, Episode {episode}")

    episode_map = {}

    # ----------------------------------
    # Previous seasons
    # ----------------------------------
    for s in range(1, season):
        count = int(input(
            f"How many episodes in Season {s}? "
        ))
        episode_map[str(s)] = list(range(1, count + 1))

    # ----------------------------------
    # Current season (auto-fill)
    # ----------------------------------
    episode_map[str(season)] = list(range(1, episode + 1))

    backend.update(
        id=row_id,
        title=title,
        value=json.dumps(episode_map),
        constant="episodes",
        comment="Converted from old format",
        workspace=workspace
    )

    print(termcolor2.colored("✔ Conversion completed", "green"))
