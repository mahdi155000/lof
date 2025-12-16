import re
import time
import threading
import json
import dbus
from dbus.mainloop.glib import DBusGMainLoop
from Asset import backend


class VLCListerner:
    def __init__(self, workspace=None):
        DBusGMainLoop(set_as_default=True)  # 🔴 REQUIRED

        self.WORKSPACE = workspace or backend.current_workspace or "lof"
        backend.connect(self.WORKSPACE)

        self.last_filename = None
        self.current_session_start = None
        self.last_identity = None  # (title, season, episode)

    # ----------------------------------
    # Title extraction
    # ----------------------------------
    @staticmethod
    def extract_title(filename: str) -> str:
        name = re.sub(r"\.[^.]+$", "", filename)
        name = re.sub(r"[sS]\d{1,2}[eE]\d{1,2}", "", name)
        name = re.sub(r"[^A-Za-z0-9 ]+", " ", name)
        name = re.sub(r"\s+", " ", name).strip()
        return name.replace(" ", "_").lower()

    # ----------------------------------
    # VLC DBus connection
    # ----------------------------------
    @staticmethod
    def find_vlc_props():
        try:
            bus = dbus.SessionBus()
            vlc_obj = bus.get_object(
                "org.mpris.MediaPlayer2.vlc",
                "/org/mpris/MediaPlayer2"
            )
            return dbus.Interface(vlc_obj, "org.freedesktop.DBus.Properties")
        except dbus.exceptions.DBusException:
            return None

    # ----------------------------------
    # Track recognition
    # ----------------------------------
    def _handle_new_track(self, metadata):
        raw = ""

        if metadata.get("xesam:title"):
            raw = str(metadata["xesam:title"])
        elif metadata.get("xesam:url"):
            raw = metadata["xesam:url"].split("/")[-1]

        raw = raw.strip()
        if not raw:
            return

        title = self.extract_title(raw)
        season, episode = self._get_season_episode(raw)

        identity = (title, season, episode)

        # Same logical media reopened → ignore
        if identity == self.last_identity:
            return

        # ---------- DECISION ----------
        already_exists = False
        if season is not None and episode is not None:
            already_exists = self._episode_exists(title, season, episode)

        # ---------- PRINT ----------
        if season is not None and episode is not None:
            if not already_exists:
                if self.last_identity and self.last_identity[0] == title:
                    old = self.last_identity
                    print(
                        f"[VLC] Updated: {title} "
                        f"S{old[1]:02}E{old[2]:02} → "
                        f"S{season:02}E{episode:02}"
                    )
                else:
                    print(
                        f"[VLC] New series detected → "
                        f"{title} S{season:02}E{episode:02}"
                    )
        else:
            if identity != self.last_identity:
                print(f"[VLC] New movie detected → {title}")

        self.last_identity = identity
        self._save_track_session(title, raw)


    def _episode_exists(self, title, season, episode):
        rows = backend.view(self.WORKSPACE)
        for row in rows:
            if row[1] == title and row[3] == "episodes":
                try:
                    ep_map = json.loads(row[2])
                except Exception:
                    return False

                return (
                    str(season) in ep_map and
                    episode in ep_map[str(season)]
                )
        return False


   # ----------------------------------
    # Save session (movies + episodes)
    # ----------------------------------
    def _save_track_session(self, title, raw_filename):
        season, episode = self._get_season_episode(raw_filename)

        rows = backend.view_with_sessions(self.WORKSPACE)
        row_match = None
        for row in rows:
            if row[1] == title:
                row_match = row
                break

        now = time.time()
        if self.current_session_start is None:
            self.current_session_start = now

        # ----------------------------
        # Existing entry
        # ----------------------------
        if row_match:
            row_id, _, value, _, _, sessions_json = row_match

            try:
                episode_map = json.loads(value) if value else {}
                sessions_list = json.loads(sessions_json)
            except Exception:
                return

            # Episodes (if exists)
            if season is not None and episode is not None:
                key = str(season)
                episode_map.setdefault(key, [])
                if episode not in episode_map[key]:
                    episode_map[key].append(episode)

            sessions_list.append({
                "start": self.current_session_start,
                "end": now,
                "duration": int(now - self.current_session_start)
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

        # ----------------------------
        # New entry
        # ----------------------------
        else:
            ep_map = {}
            if season is not None and episode is not None:
                ep_map = {str(season): [episode]}

            sess_list = [{
                "start": now,
                "end": now,
                "duration": 0
            }]

            backend.insert_json_episode(
                titile=title,
                value=json.dumps(ep_map),
                constant="episodes",
                comment="Detected via VLC",
                sessions=sess_list,
                workspace=self.WORKSPACE
            )

        self.current_session_start = now

    # ----------------------------------
    @staticmethod
    def _get_season_episode(filename: str):
        m = re.search(r"[sS](\d{1,2})[eE](\d{1,2})", filename)
        if m:
            return int(m.group(1)), int(m.group(2))
        return None, None

    # ----------------------------------
    # Background listener
    # ----------------------------------
    def listen(self):
        print("Waiting for VLC…")

        while True:
            props = self.find_vlc_props()
            if not props:
                time.sleep(1)
                continue

            print("VLC detected — tracking playback…")

            while True:
                try:
                    metadata = props.Get(
                        "org.mpris.MediaPlayer2.Player",
                        "Metadata"
                    )
                    self._handle_new_track(metadata)
                    time.sleep(1)
                except dbus.exceptions.DBusException:
                    print("VLC closed — waiting…")
                    self.last_filename = None
                    self.current_session_start = None
                    break

    def start_in_background(self):
        threading.Thread(
            target=self.listen,
            daemon=True
        ).start()
