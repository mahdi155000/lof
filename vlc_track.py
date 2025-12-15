#!/usr/bin/env python3

import re
import time
import dbus
from dbus.mainloop.glib import DBusGMainLoop
from Asset import backend

WORKSPACE = backend.current_workspace or "lof"
backend.connect(WORKSPACE)

def extract_title(filename: str) -> str:
    """Extract cleaned title without season/episode."""
    name = re.sub(r"\.[^.]+$", "", filename)
    name = re.sub(r"[sS]\d{1,2}[eE]\d{1,2}", "", name)
    name = re.sub(r"[^A-Za-z0-9 ]+", " ", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name.replace(" ", "_").lower()

def extract_season_episode(filename: str):
    """Extract season and episode numbers from filename as integers."""
    match = re.search(r"[sS](\d{1,2})[eE](\d{1,2})", filename)
    if match:
        season, episode = match.groups()
        return int(season), int(episode)
    return None, None

def save_or_insert_title(title: str, filename: str):
    """Update existing row if exact title exists, else insert new row at the end."""
    season, episode = extract_season_episode(filename)
    season_val = season if season is not None else ""
    episode_val = episode if episode is not None else ""

    # Get all entries in the workspace
    all_entries = backend.view(WORKSPACE)

    # Look for an exact match
    exact_match = None
    for row in all_entries:
        row_id, row_title, _, _, _ = row
        if row_title == title:
            exact_match = row
            break

    if exact_match:
        # Update the existing row with this title
        row_id = exact_match[0]
        backend.update(
            id=row_id,
            title=title,
            value=episode_val,
            constant=season_val,
            comment="Detected via VLC",
            workspace=WORKSPACE
        )
        print(f"Updated existing entry: {title} -> Season: {season_val}, Episode: {episode_val}")
    else:
        # Insert new row at the end
        backend.insert(
            titile=title,
            value=episode_val,
            constant=season_val,
            comment="Detected via VLC",
            workspace=WORKSPACE
        )
        print(f"Inserted new entry at end: {title} -> Season: {season_val}, Episode: {episode_val}")

def find_vlc_player(session_bus):
    try:
        vlc_obj = session_bus.get_object(
            "org.mpris.MediaPlayer2.vlc",
            "/org/mpris/MediaPlayer2"
        )
        return dbus.Interface(vlc_obj, "org.freedesktop.DBus.Properties")
    except dbus.exceptions.DBusException:
        return None

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
                        extracted_title = extract_title(raw_filename)
                        print(f"\nDetected file: {raw_filename}")
                        print(f"Extracted title suggestion: {extracted_title}")
                        user_input = input(
                            "Press Enter to accept, or type a corrected title: "
                        ).strip()
                        confirmed_title = user_input if user_input else extracted_title
                        save_or_insert_title(confirmed_title, raw_filename)
                time.sleep(1)
            except dbus.exceptions.DBusException:
                print("\nVLC closed — waiting for it to reopen…")
                last_track = None
                break

if __name__ == "__main__":
    listen_vlc()