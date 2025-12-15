#!/usr/bin/env python3

import re
import time
import dbus
from dbus.mainloop.glib import DBusGMainLoop

# --------------------------------------------------
# Import your backend correctly
# --------------------------------------------------
from Asset import backend

# Use current workspace defined by backend
WORKSPACE = backend.current_workspace or "lof"

# Ensure workspace table exists
backend.connect(WORKSPACE)

# --------------------------------------------------
# Helpers
# --------------------------------------------------
def extract_title(filename: str) -> str:
    """Extracts cleaned title like 'ben_10_alien_force'."""
    name = re.sub(r"\.[^.]+$", "", filename)
    name = re.sub(r"[sS]\d{1,2}[eE]\d{1,2}", "", name)
    name = re.sub(r"[^A-Za-z0-9 ]+", " ", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name.replace(" ", "_").lower()


def save_title(confirmed: str, raw: str):
    """
    Save using Asset/backend.py rules:
    title    -> confirmed title
    value    -> raw filename
    constant -> source tag
    comment  -> note
    """
    backend.insert(
        titile=confirmed,
        value=raw,
        constant="vlc",
        comment="Detected via VLC",
        workspace=WORKSPACE
    )


def find_vlc_player(session_bus):
    """Try to find a running VLC MPRIS service."""
    try:
        vlc_obj = session_bus.get_object(
            "org.mpris.MediaPlayer2.vlc",
            "/org/mpris/MediaPlayer2"
        )
        return dbus.Interface(vlc_obj, "org.freedesktop.DBus.Properties")
    except dbus.exceptions.DBusException:
        return None


# --------------------------------------------------
# VLC listener
# --------------------------------------------------
def listen_vlc():
    DBusGMainLoop(set_as_default=True)
    session_bus = dbus.SessionBus()

    last_track = None

    print("Waiting for VLC to start...")

    while True:
        props = find_vlc_player(session_bus)

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

                if track_id and track_id != last_track:
                    last_track = track_id

                    raw_filename = ""
                    if metadata.get("xesam:title"):
                        raw_filename = str(metadata["xesam:title"])
                    elif metadata.get("xesam:url"):
                        raw_filename = metadata["xesam:url"].split("/")[-1]

                    raw_filename = raw_filename.strip()

                    if raw_filename:
                        extracted = extract_title(raw_filename)

                        print(f"\nDetected file: {raw_filename}")
                        print(f"Extracted title suggestion: {extracted}")

                        user_input = input(
                            "Press Enter to accept, or type a corrected title: "
                        ).strip()

                        confirmed = user_input if user_input else extracted

                        save_title(confirmed, raw_filename)

                        print(
                            f"Saved to workspace '{WORKSPACE}': {confirmed}"
                        )

                time.sleep(1)

            except dbus.exceptions.DBusException:
                print("\nVLC closed — waiting for it to reopen…")
                last_track = None
                break


# --------------------------------------------------
if __name__ == "__main__":
    listen_vlc()
