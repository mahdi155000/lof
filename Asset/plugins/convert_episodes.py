from plugin import plugin, register_help
from Asset import backend
from workspace_manager_module import workspace_manager
import json
import termcolor2


@register_help
@plugin("convert_episodes")
def convert_episodes():
    """
    Convert old episode format (single episode number)
    into new episode-map format (Option A).
    """

    workspace = workspace_manager.current_workspace
    rows = backend.view(workspace)

    converted = 0
    skipped = 0

    for row in rows:
        row_id, title, value, constant, comment = row

        # Try to detect already converted entries
        try:
            if isinstance(value, (str, bytes)):
                json.loads(value)
                skipped += 1
                continue
        except Exception:
            pass

        # Old format must have integer season & episode
        try:
            season = int(constant)
            episode = int(value)
        except Exception:
            skipped += 1
            continue

        # Build episode map
        episode_map = {
            str(season): list(range(1, episode + 1))
        }

        # Serialize to JSON
        serialized = json.dumps(episode_map)

        backend.update(
            id=row_id,
            title=title,
            value=serialized,
            constant=str(season),
            comment="Migrated to episode map format",
            workspace=workspace
        )

        converted += 1
        termcolor2.colored(
            f"Converted: {title} | S{season} up to E{episode}",
            "green"
        )

    termcolor2.colored(
        f"\nDone. Converted: {converted}, Skipped: {skipped}",
        "cyan"
    )
