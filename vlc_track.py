import re
import time
import threading
import json
import dbus
from dbus.mainloop.glib import DBusGMainLoop
from Asset import backend


class VLCListerner:
    def __init__(self, workspace=None):
        self.WORKSPACE = workspace or backend.current_workspace or "lof"
        backend.connect(self.WORKSPACE)
        self.last_track = None
        self.current_session_start = None

    # --------------------------------------------------
    # Filename parsing
    # --------------------------------------------------
    @staticmethod
    def extract_title(filename: str) -> str:
        """Extract cleaned title without season/episode."""
        name = re.sub(r"\.[^.]+$", "", filename)
        name = re.sub(r"[sS]\d{1,2}[eE]\d{1,2}", "", name)
        name = re.sub(r"[^A-Za-z0-9 ]+", " ", name)
        name = re.sub(r"\s+", " ", name).strip()
        return name.replace(" ", "_").lower()

    @staticmethod
    def extract_season_episode(filename: str):
        """Extract season and episode numbers."""
        match = re.search(r"[sS](\d{1,2})[eE](\d{1,2})", filename)
        if match:
            return int(match.group(1)), int(match.group(2))
        return None, None

    # --------------------------------------------------
    # Core logic (JSON episode map + sessions)
    # --------------------------------------------------
    def save_or_update_sequential(self, title: str, filename: str):
        season, episode = self.extract_season_episode(filename)
        if season is None or episode is None:
            return

        rows = backend.view_with_sessions(self.WORKSPACE)
        row_match = None

        for row in rows:
            if row[1] == title:
                row_match = row
                break

        # New session timing
        now = time.time()

        if self.current_session_start is None:
            self.current_session_start = now

        # --------------------------------------------------
        # EXISTING TITLE
        # --------------------------------------------------
        if row_match:
            row_id, _, value, _, _, sessions_json = row_match
            try:
                episode_map = json.loads(value)
            except Exception:
                print(f"Skipped (invalid JSON): {title}")
                return

            try:
                sessions_list = json.loads(sessions_json)
            except Exception:
                sessions_list = []

            season_key = str(season)

            # Add missing past episodes automatically
            if season_key not in episode_map:
                episode_map[season_key] = list(range(1, episode + 1))
            else:
                last_episode = max(episode_map[season_key])
                if episode > last_episode:
                    episode_map[season_key].append(episode)
                else:
                    print(f"Skipped: {title} S{season}E{episode} (already exists)")
                    return

            # Record session time
            sessions_list.append({"start": self.current_session_start, "end": now, "duration": now - self.current_session_start})
            self.current_session_start = now

            backend.update_json_episode(
                id=row_id,
                title=title,
                value=json.dumps(episode_map),
                constant="episodes",
                comment="Detected via VLC",
                sessions=sessions_list,
                workspace=self.WORKSPACE
            )

            print(f"Updated: {title} -> S{season}E{episode}")
            return

        # --------------------------------------------------
        # NEW TITLE → INSERT AT END
        # --------------------------------------------------
        episode_map = {str(season): [episode]}
        sessions_list = [{"start": now, "end": now, "duration": 0}]
        backend.insert_json_episode(
            titile=title,
            value=json.dumps(episode_map),
            constant="episodes",
            comment="Detected via VLC",
            sessions=sessions_list,
            workspace=self.WORKSPACE
        )

        print(f"Inserted new entry: {title} -> S{season}E{episode}")

    # --------------------------------------------------
    # VLC DBus handling
    # --------------------------------------------------
    @staticmethod
    def find_vlc_player(session_bus):
        try:
            vlc_obj = session_bus.get_object(
                "org.mpris.MediaPlayer2.vlc",
                "/org/mpris/MediaPlayer2"
            )
            return dbus.Interface(vlc_obj, "org.freedesktop.DBus.Properties")
        except dbus.exceptions.DBusException:
            return None

    def listen(self):
        DBusGMainLoop(set_as_default=True)
        session_bus = dbus.SessionBus()

        print("Waiting for VLC to start...")

        while True:
            props = self.find_vlc_player(session_bus)
            if props is None:
                time.sleep(1)
                continue

            print("VLC detected! Listening for new tracks…")

            while True:
                try:
                    metadata = props.Get(
                        "org.mpris.MediaPlayer2.Player",
                        "Metadata"
                    )

                    track_id = metadata.get("mpris:trackid")
                    if track_id and track_id != self.last_track:
                        self.last_track = track_id

                        raw_filename = ""
                        if metadata.get("xesam:title"):
                            raw_filename = str(metadata["xesam:title"])
                        elif metadata.get("xesam:url"):
                            raw_filename = metadata["xesam:url"].split("/")[-1]

                        raw_filename = raw_filename.strip()
                        if raw_filename:
                            title = self.extract_title(raw_filename)
                            print(f"\nDetected: {raw_filename}")
                            print(f"Title: {title}")
                            self.save_or_update_sequential(title, raw_filename)

                    time.sleep(1)

                except dbus.exceptions.DBusException:
                    print("\nVLC closed — waiting…")
                    self.last_track = None
                    break

    def start_in_background(self):
        thread = threading.Thread(target=self.listen, daemon=True)
        thread.start()
