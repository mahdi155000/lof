# vlc_tracker.py
import re
import time
import threading
import dbus
from dbus.mainloop.glib import DBusGMainLoop
from Asset import backend

class VLCListerner:
    def __init__(self, workspace=None):
        self.WORKSPACE = workspace or backend.current_workspace or "lof"
        backend.connect(self.WORKSPACE)
        self.last_track = None

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
        """Extract season and episode numbers from filename as integers."""
        match = re.search(r"[sS](\d{1,2})[eE](\d{1,2})", filename)
        if match:
            season, episode = match.groups()
            return int(season), int(episode)
        return None, None

    def save_or_update_sequential(self, title: str, filename: str):
        season, episode = self.extract_season_episode(filename)
        if season is None or episode is None:
            return

        all_entries = backend.view(self.WORKSPACE)
        exact_match = None
        for row in all_entries:
            row_id, row_title, row_value, row_constant, _ = row
            if row_title == title:
                exact_match = row
                break

        if exact_match:
            current_season = int(exact_match[3])
            current_episode = int(exact_match[2])

            if season == current_season and episode == current_episode + 1:
                backend.update(
                    id=exact_match[0],
                    title=title,
                    value=episode,
                    constant=season,
                    comment="Detected via VLC",
                    workspace=self.WORKSPACE
                )
                print(f"Updated entry: {title} -> Season: {season}, Episode: {episode}")
            elif season == (current_season + 1) and episode == 1:
                backend.update(
                    id=exact_match[0],
                    title=title,
                    value=1,
                    constant=season,
                    comment="Detected via VLC",
                    workspace=self.WORKSPACE
                )
                print(f"Updated entry: {title} -> NEW Season: {season}, Episode {episode}")
            else:
                print(f"Skipped: {title} -> Season: {season}, Episode: {episode} (not sequential)")
        else:
            backend.insert(
                titile=title,
                value=episode,
                constant=season,
                comment="Detected via VLC",
                workspace=self.WORKSPACE
            )
            print(f"Inserted new entry at end: {title} -> Season: {season}, Episode: {episode}")

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
                            extracted_title = self.extract_title(raw_filename)
                            print(f"\nDetected file: {raw_filename}")
                            print(f"Extracted title suggestion: {extracted_title}")
                            # Auto-confirm without user input
                            self.save_or_update_sequential(extracted_title, raw_filename)
                    time.sleep(1)
                except dbus.exceptions.DBusException:
                    print("\nVLC closed — waiting for it to reopen…")
                    self.last_track = None
                    break

    def start_in_background(self):
        """Run the VLC listener in a separate thread."""
        thread = threading.Thread(target=self.listen, daemon=True)
        thread.start()
