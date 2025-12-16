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

    @staticmethod
    def extract_title(filename: str) -> str:
        """Clean title without season/episode."""
        name = re.sub(r"\.[^.]+$", "", filename)
        name = re.sub(r"[sS]\d{1,2}[eE]\d{1,2}", "", name)
        name = re.sub(r"[^A-Za-z0-9 ]+", " ", name)
        name = re.sub(r"\s+", " ", name).strip()
        return name.replace(" ", "_").lower()

    # -------------------------------
    # VLC DBus connection
    # -------------------------------
    @staticmethod
    def find_vlc_props():
        try:
            session_bus = dbus.SessionBus()
            vlc_obj = session_bus.get_object(
                "org.mpris.MediaPlayer2.vlc",
                "/org/mpris/MediaPlayer2"
            )
            return dbus.Interface(vlc_obj, "org.freedesktop.DBus.Properties")
        except dbus.exceptions.DBusException:
            return None

    # -------------------------------
    # On-demand status
    # -------------------------------
    def get_status(self):
        props = self.find_vlc_props()
        if not props:
            return None

        try:
            metadata = props.Get("org.mpris.MediaPlayer2.Player", "Metadata")
            status = props.Get("org.mpris.MediaPlayer2.Player", "PlaybackStatus")
            position_us = props.Get("org.mpris.MediaPlayer2.Player", "Position")
        except dbus.exceptions.DBusException:
            return None

        # Current playback position (always available)
        position_sec = position_us / 1_000_000

        # Try to read duration from mpris-length
        duration_us = metadata.get("mpris:length", 0)
        if duration_us:
            duration_sec = duration_us / 1_000_000
        else:
            # VLC’s MPRIS often doesn’t provide duration for videos; treat as unknown
            duration_sec = None

        raw = ""
        if metadata.get("xesam:title"):
            raw = str(metadata["xesam:title"])
        elif metadata.get("xesam:url"):
            raw = metadata["xesam:url"].split("/")[-1]
        raw = raw.strip()

        return {
            "status": status,
            "position": position_sec,
            "duration": duration_sec,
            "filename": raw
        }


    # -------------------------------
    # Track recognition logic
    # -------------------------------
    def _handle_new_track(self, metadata):
        raw_filename = ""
        if metadata.get("xesam:title"):
            raw_filename = str(metadata["xesam:title"])
        elif metadata.get("xesam:url"):
            raw_filename = metadata["xesam:url"].split("/")[-1]
        raw_filename = raw_filename.strip()
        if not raw_filename:
            return

        track_id = metadata.get("mpris:trackid")
        if track_id and track_id != self.last_track:
            self.last_track = track_id
            title = self.extract_title(raw_filename)
            self._save_track_session(title, raw_filename)

    def _save_track_session(self, title, raw_filename):
        season, episode = self._get_season_episode(raw_filename)
        if season is None or episode is None:
            return

        rows = backend.view_with_sessions(self.WORKSPACE)
        row_match = None
        for row in rows:
            if row[1] == title:
                row_match = row
                break

        now = time.time()
        if self.current_session_start is None:
            self.current_session_start = now

        if row_match:
            row_id, _, value, _, _, sessions_json = row_match
            try:
                episode_map = json.loads(value)
                sessions_list = json.loads(sessions_json)
            except:
                return

            key = str(season)
            if key not in episode_map:
                episode_map[key] = [episode]
            else:
                if episode not in episode_map[key]:
                    episode_map[key].append(episode)

            sessions_list.append({
                "start": self.current_session_start,
                "end": now,
                "duration": now - self.current_session_start
            })

            backend.update_json_episode(
                id=row_id,
                title=title,
                value=json.dumps(episode_map),
                constant="episodes",
                comment="Detected via VLC",
                sessions=sessions_list,
                workspace=self.WORKSPACE
            )
            self.current_session_start = now

        else:
            ep_map = {str(season): [episode]}
            sess_list = [{"start": now, "end": now, "duration": 0}]
            backend.insert_json_episode(
                titile=title,
                value=json.dumps(ep_map),
                constant="episodes",
                comment="Detected via VLC",
                sessions=sess_list,
                workspace=self.WORKSPACE
            )
            self.current_session_start = now

    @staticmethod
    def _get_season_episode(filename: str):
        m = re.search(r"[sS](\d{1,2})[eE](\d{1,2})", filename)
        if m:
            return int(m.group(1)), int(m.group(2))
        return None, None

    # -------------------------------
    # Background listener for track changes
    # -------------------------------
    def listen(self):
        DBusGMainLoop(set_as_default=True)
        print("Waiting for VLC…")
        while True:
            props = self.find_vlc_props()
            if not props:
                time.sleep(1)
                continue

            print("VLC detected — listening for new tracks…")
            while True:
                try:
                    metadata = props.Get("org.mpris.MediaPlayer2.Player", "Metadata")
                    self._handle_new_track(metadata)
                    time.sleep(1)
                except dbus.exceptions.DBusException:
                    print("VLC closed — waiting…")
                    self.last_track = None
                    break

    def start_in_background(self):
        thread = threading.Thread(target=self.listen, daemon=True)
        thread.start()
