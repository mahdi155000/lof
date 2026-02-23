"""Cross-platform GUI for LOF using Kivy (Linux + Android)."""
import json
import os
from functools import partial

from Asset import backend
from workspace_manager_module import workspace_manager

from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.utils import platform

try:
    import requests
except ImportError:
    requests = None


THEME = {
    "bg": (0.06, 0.08, 0.12, 1),
    "panel": (0.1, 0.13, 0.18, 0.96),
    "panel_soft": (0.12, 0.16, 0.23, 0.9),
    "text": (0.92, 0.95, 1, 1),
    "muted": (0.68, 0.74, 0.84, 1),
    "accent": (0.12, 0.67, 0.55, 1),
    "accent_2": (0.2, 0.58, 0.9, 1),
    "danger": (0.86, 0.3, 0.3, 1),
    "chip": (0.14, 0.2, 0.3, 1),
}

DEFAULT_SERVER_URL = os.environ.get("LOF_SERVER_URL", "http://192.168.1.100:5000")
LOCAL_DB_PATH = os.path.join("Asset", "list_of_work.db")


def start_vlc_tracker_if_available():
    """Start VLC listener on Linux only, without breaking Android runtime."""
    if platform != "linux":
        return
    if workspace_manager.current_workspace != "lof":
        return
    try:
        from vlc_track import VLCListerner  # pylint: disable=import-outside-toplevel
        vlc_listener = VLCListerner()
        vlc_listener.start_in_background()
    except Exception:
        pass


class ThemedButton(Button):
    def __init__(self, bg, fg=None, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_down = ""
        self.background_color = bg
        self.color = fg or THEME["text"]
        self.bold = True
        self.font_size = "14sp"


class Card(BoxLayout):
    def __init__(self, color, radius=16, **kwargs):
        super().__init__(**kwargs)
        self._color = color
        self._radius = radius
        with self.canvas.before:
            self._card_color = Color(*self._color)
            self._card_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self._radius] * 4)
        self.bind(pos=self._sync_graphics, size=self._sync_graphics)

    def _sync_graphics(self, *_):
        self._card_rect.pos = self.pos
        self._card_rect.size = self.size


class ThemedInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.multiline = False
        self.background_normal = ""
        self.background_active = ""
        self.background_color = THEME["panel_soft"]
        self.foreground_color = THEME["text"]
        self.cursor_color = THEME["accent"]
        self.hint_text_color = THEME["muted"]
        self.padding = [dp(12), dp(10), dp(12), dp(10)]
        self.font_size = "15sp"


class DataSourceManager:
    """Handle local/server DB access using existing API endpoints."""

    def __init__(self, server_url=DEFAULT_SERVER_URL, local_db_path=LOCAL_DB_PATH):
        self.server_url = server_url.rstrip("/")
        self.local_db_path = local_db_path

    def set_server_url(self, server_url):
        self.server_url = (server_url or "").rstrip("/")

    def _has_requests(self):
        return requests is not None

    def download_db(self):
        if not self._has_requests():
            return False, "requests package is not installed."
        if not self.server_url:
            return False, "Server URL is empty."
        try:
            response = requests.get(f"{self.server_url}/api/download_db", timeout=10)
            response.raise_for_status()
            with open(self.local_db_path, "wb") as db_file:
                db_file.write(response.content)
            return True, "Pulled server DB -> local."
        except Exception as exc:
            return False, f"Pull failed: {exc}"

    def upload_db(self):
        if not self._has_requests():
            return False, "requests package is not installed."
        if not self.server_url:
            return False, "Server URL is empty."
        if not os.path.isfile(self.local_db_path):
            return False, f"Local DB not found: {self.local_db_path}"
        try:
            with open(self.local_db_path, "rb") as db_file:
                files = {"dbfile": db_file}
                response = requests.post(f"{self.server_url}/api/upload_db", files=files, timeout=10)
            response.raise_for_status()
            return True, "Pushed local DB -> server."
        except Exception as exc:
            return False, f"Push failed: {exc}"


class LofRoot(BoxLayout):
    """Main dashboard and CRUD actions."""

    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", spacing=dp(10), padding=dp(12), **kwargs)
        self.selected_category = "tasks"
        self.data_mode = "local"
        self.items = []
        self.category_buttons = {}
        self.source_buttons = {}
        self.workspace_names = []
        self._updating_workspace_spinner = False
        self.data_source = DataSourceManager()

        self._paint_background()
        self._build_ui()
        self.switch_workspace()
        self.refresh_list()

    def _paint_background(self):
        with self.canvas.before:
            Color(*THEME["bg"])
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
            Color(0.14, 0.45, 0.74, 0.12)
            self.shape_1 = Ellipse(size=(dp(360), dp(360)), pos=(self.x - dp(70), self.top - dp(250)))
            Color(0.15, 0.68, 0.6, 0.11)
            self.shape_2 = Ellipse(size=(dp(420), dp(420)), pos=(self.right - dp(260), self.y - dp(170)))
        self.bind(pos=self._sync_background, size=self._sync_background)

    def _sync_background(self, *_):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.shape_1.pos = (self.x - dp(70), self.top - dp(250))
        self.shape_2.pos = (self.right - dp(260), self.y - dp(170))

    def _build_ui(self):
        header = Card(
            THEME["panel"],
            orientation="vertical",
            padding=dp(14),
            spacing=dp(10),
            size_hint_y=None,
            height=dp(248),
        )

        header_top = BoxLayout(size_hint_y=None, height=dp(32))
        title = Label(
            text="[b]LOF[/b]  [size=16]Daily Tracker[/size]",
            markup=True,
            color=THEME["text"],
            halign="left",
            valign="middle",
        )
        title.bind(size=self._label_size)
        self.count_label = Label(
            text="0 items",
            color=THEME["muted"],
            size_hint_x=0.3,
            halign="right",
            valign="middle",
        )
        self.count_label.bind(size=self._label_size)
        header_top.add_widget(title)
        header_top.add_widget(self.count_label)
        header.add_widget(header_top)

        workspace_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        self.workspace_input = ThemedInput(
            text=workspace_manager.current_workspace or "lof",
            hint_text="Workspace name",
        )
        self.workspace_spinner = Spinner(
            text="Choose workspace",
            values=(),
            size_hint_x=0.42,
            background_normal="",
            background_color=THEME["panel_soft"],
            color=THEME["text"],
            sync_height=True,
        )
        self.workspace_spinner.bind(text=self.on_workspace_selected)
        workspace_btn = ThemedButton(
            text="Switch",
            bg=THEME["accent_2"],
            size_hint_x=0.2,
        )
        refresh_ws_btn = ThemedButton(
            text="Refresh",
            bg=(0.17, 0.55, 0.72, 1),
            size_hint_x=0.2,
        )
        workspace_btn.bind(on_press=lambda *_: self.switch_workspace())
        refresh_ws_btn.bind(on_press=lambda *_: self.refresh_workspace_options())
        workspace_row.add_widget(self.workspace_input)
        workspace_row.add_widget(self.workspace_spinner)
        workspace_row.add_widget(workspace_btn)
        workspace_row.add_widget(refresh_ws_btn)
        header.add_widget(workspace_row)

        server_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        self.server_input = ThemedInput(
            text=DEFAULT_SERVER_URL,
            hint_text="Server URL: http://host:5000",
        )
        server_btn = ThemedButton(
            text="Set Server",
            bg=(0.2, 0.48, 0.75, 1),
            size_hint_x=0.28,
        )
        server_btn.bind(on_press=lambda *_: self.set_server_url())
        server_row.add_widget(self.server_input)
        server_row.add_widget(server_btn)
        header.add_widget(server_row)

        mode_row = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(8))
        for mode, title in (("local", "Local"), ("server", "Server"), ("both", "Both Sync")):
            btn = ThemedButton(text=title, bg=THEME["chip"])
            btn.bind(on_press=partial(self.set_data_mode, mode))
            mode_row.add_widget(btn)
            self.source_buttons[mode] = btn
        header.add_widget(mode_row)

        sync_row = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(8))
        pull_btn = ThemedButton(text="Pull", bg=(0.17, 0.55, 0.72, 1))
        push_btn = ThemedButton(text="Push", bg=(0.14, 0.63, 0.48, 1))
        pull_btn.bind(on_press=lambda *_: self.manual_pull())
        push_btn.bind(on_press=lambda *_: self.manual_push())
        sync_row.add_widget(pull_btn)
        sync_row.add_widget(push_btn)
        header.add_widget(sync_row)

        self.add_widget(header)
        self._refresh_source_chips()
        self.refresh_workspace_options()

        chips = Card(
            THEME["panel"],
            orientation="horizontal",
            spacing=dp(8),
            padding=dp(10),
            size_hint_y=None,
            height=dp(60),
        )
        for category in ("tasks", "movies", "books", "all"):
            btn = ThemedButton(
                text=category.capitalize(),
                bg=THEME["chip"],
                size_hint_x=0.25,
            )
            btn.bind(on_press=partial(self.change_category, category))
            chips.add_widget(btn)
            self.category_buttons[category] = btn
        self.add_widget(chips)
        self._refresh_category_chips()

        form_card = Card(
            THEME["panel"],
            orientation="vertical",
            spacing=dp(8),
            padding=dp(10),
            size_hint_y=None,
            height=dp(170),
        )
        form_title = Label(
            text="Create New Item",
            color=THEME["muted"],
            size_hint_y=None,
            height=dp(20),
            halign="left",
            valign="middle",
        )
        form_title.bind(size=self._label_size)
        form_card.add_widget(form_title)

        row_1 = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        self.title_input = ThemedInput(hint_text="Title")
        self.value_input = ThemedInput(hint_text="Value (number or text)")
        row_1.add_widget(self.title_input)
        row_1.add_widget(self.value_input)
        form_card.add_widget(row_1)

        row_2 = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        self.constant_input = ThemedInput(hint_text="Type: tasks / movies / books")
        self.comment_input = ThemedInput(hint_text="Comment")
        row_2.add_widget(self.constant_input)
        row_2.add_widget(self.comment_input)
        form_card.add_widget(row_2)

        add_btn = ThemedButton(text="Add Item", bg=THEME["accent"], size_hint_y=None, height=dp(42))
        add_btn.bind(on_press=lambda *_: self.add_item())
        form_card.add_widget(add_btn)
        self.add_widget(form_card)

        list_header = BoxLayout(size_hint_y=None, height=dp(24))
        list_title = Label(
            text="Items",
            color=THEME["muted"],
            halign="left",
            valign="middle",
        )
        list_title.bind(size=self._label_size)
        list_header.add_widget(list_title)
        self.add_widget(list_header)

        self.list_scroll = ScrollView(bar_width=dp(6), scroll_type=["bars", "content"])
        self.list_layout = GridLayout(cols=1, spacing=dp(8), size_hint_y=None, padding=[0, 0, 0, dp(12)])
        self.list_layout.bind(minimum_height=self.list_layout.setter("height"))
        self.list_scroll.add_widget(self.list_layout)
        self.add_widget(self.list_scroll)

        self.log_label = Label(
            text="Ready",
            color=THEME["muted"],
            size_hint_y=None,
            height=dp(30),
            halign="left",
            valign="middle",
        )
        self.log_label.bind(size=self._label_size)
        self.add_widget(self.log_label)

    def _label_size(self, label, _):
        label.text_size = label.size

    def log(self, message):
        self.log_label.text = message

    def _refresh_category_chips(self):
        for category, btn in self.category_buttons.items():
            btn.background_color = THEME["accent_2"] if category == self.selected_category else THEME["chip"]

    def _refresh_source_chips(self):
        for mode, btn in self.source_buttons.items():
            btn.background_color = THEME["accent"] if mode == self.data_mode else THEME["chip"]

    def set_server_url(self):
        server_url = self.server_input.text.strip()
        self.data_source.set_server_url(server_url)
        self.log(f"Server: {server_url or '(empty)'}")

    def set_data_mode(self, mode, *_):
        self.set_server_url()
        self.data_mode = mode
        self._refresh_source_chips()

        if mode == "server":
            ok, message = self.data_source.download_db()
            self.log(message)
            if ok:
                self.switch_workspace()
                return

        self.log(f"Mode: {mode}")
        self.refresh_list()

    def manual_pull(self):
        self.set_server_url()
        ok, message = self.data_source.download_db()
        self.log(message)
        if ok:
            self.refresh_workspace_options()
            self.switch_workspace()

    def manual_push(self):
        self.set_server_url()
        ok, message = self.data_source.upload_db()
        self.log(message)

    def _sync_before_read(self):
        if self.data_mode != "server":
            return
        ok, message = self.data_source.download_db()
        if not ok:
            self.log(message)

    def _sync_after_write(self):
        if self.data_mode not in {"server", "both"}:
            return
        ok, message = self.data_source.upload_db()
        if not ok:
            self.log(message)
        else:
            self.log(f"{message} (mode: {self.data_mode})")

    def switch_workspace(self):
        workspace = (self.workspace_input.text or "lof").strip()
        workspace_manager.switch_workspace(workspace)
        backend.switch_workspace(workspace)
        backend.connect(workspace)
        self.refresh_workspace_options()
        if workspace in self.workspace_names:
            self._updating_workspace_spinner = True
            self.workspace_spinner.text = workspace
            self._updating_workspace_spinner = False
        self.log(f"Workspace: {workspace}")
        self.refresh_list()

    def refresh_workspace_options(self):
        try:
            tables = sorted(backend.list_tables())
        except Exception as exc:
            self.log(f"Workspace list failed: {exc}")
            return

        self.workspace_names = [table for table in tables if not table.startswith("sqlite_")]
        if not self.workspace_names:
            self.workspace_names = ["lof"]

        self.workspace_spinner.values = tuple(self.workspace_names)
        current_workspace = workspace_manager.current_workspace or "lof"
        if current_workspace in self.workspace_names:
            selected = current_workspace
        else:
            selected = self.workspace_names[0]

        self._updating_workspace_spinner = True
        self.workspace_spinner.text = selected
        self._updating_workspace_spinner = False

    def on_workspace_selected(self, _spinner, selected_workspace):
        if self._updating_workspace_spinner:
            return
        if not selected_workspace or selected_workspace == "Choose workspace":
            return
        self.workspace_input.text = selected_workspace
        self.switch_workspace()

    def change_category(self, category, *_):
        self.selected_category = category
        self._refresh_category_chips()
        self.refresh_list()
        self.log(f"Category: {category}")

    def _category_of(self, item):
        _, _, _, constant, _, _ = self._unpack_item(item)
        constant = str(constant or "").lower().strip()
        if constant in {"task", "tasks", "todo", "to-do"}:
            return "tasks"
        if constant in {"movie", "movies", "film", "episode", "episodes"}:
            return "movies"
        if constant in {"book", "books", "read", "reading"}:
            return "books"
        return "tasks"

    @staticmethod
    def _unpack_item(item):
        """Return a normalized 6-field tuple for DB rows.

        Supports legacy rows (5 fields) and rows with sessions (6 fields).
        """
        item_id = item[0]
        title = item[1]
        value = item[2]
        constant = item[3] if len(item) > 3 else ""
        comment = item[4] if len(item) > 4 else ""
        sessions = item[5] if len(item) > 5 else None
        return item_id, title, value, constant, comment, sessions

    def _format_value(self, value, constant):
        if str(constant).lower() == "episodes":
            try:
                episode_map = json.loads(value)
                if not episode_map:
                    return "No episodes"
                last_season = str(max(int(season) for season in episode_map.keys()))
                last_episode = max(episode_map[last_season])
                return f"S{int(last_season):02}E{int(last_episode):02}"
            except Exception:
                return str(value)
        return str(value)

    def _create_item_row(self, item):
        item_id, title, value, constant, comment, _ = self._unpack_item(item)
        value_text = self._format_value(value, constant)

        card = Card(
            THEME["panel_soft"],
            orientation="horizontal",
            spacing=dp(8),
            padding=dp(8),
            size_hint_y=None,
            height=dp(74),
        )

        info_col = BoxLayout(orientation="vertical", spacing=dp(2))
        title_lbl = Label(
            text=f"[b]{item_id}. {title}[/b]",
            markup=True,
            color=THEME["text"],
            halign="left",
            valign="middle",
        )
        title_lbl.bind(size=self._label_size)

        meta_comment = str(comment).strip() if str(comment).strip() else "-"
        meta_lbl = Label(
            text=f"[color=#9FB8D6]{constant}[/color]   [color=#D2DDEE]Value:[/color] {value_text}   [color=#D2DDEE]Comment:[/color] {meta_comment}",
            markup=True,
            color=THEME["muted"],
            halign="left",
            valign="middle",
            font_size="13sp",
        )
        meta_lbl.bind(size=self._label_size)
        info_col.add_widget(title_lbl)
        info_col.add_widget(meta_lbl)

        action_col = BoxLayout(orientation="horizontal", size_hint_x=0.46, spacing=dp(6))
        plus_btn = ThemedButton(text="+", bg=THEME["accent"], size_hint_x=0.15)
        minus_btn = ThemedButton(text="-", bg=(0.18, 0.45, 0.72, 1), size_hint_x=0.15)
        edit_btn = ThemedButton(text="Edit", bg=(0.42, 0.39, 0.68, 1), size_hint_x=0.33)
        del_btn = ThemedButton(text="Delete", bg=THEME["danger"], size_hint_x=0.37)

        plus_btn.bind(on_press=partial(self.bump_value, item, 1))
        minus_btn.bind(on_press=partial(self.bump_value, item, -1))
        edit_btn.bind(on_press=partial(self.open_edit_popup, item))
        del_btn.bind(on_press=partial(self.delete_item, item_id))

        action_col.add_widget(plus_btn)
        action_col.add_widget(minus_btn)
        action_col.add_widget(edit_btn)
        action_col.add_widget(del_btn)

        card.add_widget(info_col)
        card.add_widget(action_col)
        return card

    def refresh_list(self):
        self._sync_before_read()
        try:
            all_items = backend.view(workspace_manager.current_workspace)
        except Exception as exc:
            self.log(f"Load failed: {exc}")
            return

        self.items = []
        for item in all_items:
            if self.selected_category == "all" or self._category_of(item) == self.selected_category:
                self.items.append(item)

        self.count_label.text = f"{len(self.items)} items"
        self.list_layout.clear_widgets()

        if not self.items:
            empty = Card(
                THEME["panel_soft"],
                orientation="horizontal",
                size_hint_y=None,
                height=dp(64),
                padding=dp(12),
            )
            msg = Label(
                text="No items in this category.",
                color=THEME["muted"],
                halign="left",
                valign="middle",
            )
            msg.bind(size=self._label_size)
            empty.add_widget(msg)
            self.list_layout.add_widget(empty)
            return

        for item in self.items:
            self.list_layout.add_widget(self._create_item_row(item))

    def add_item(self):
        title = self.title_input.text.strip()
        value = self.value_input.text.strip()
        constant = self.constant_input.text.strip() or self.selected_category
        comment = self.comment_input.text.strip()

        if not title:
            self.log("Title is required.")
            return

        if value.isdigit():
            value = int(value)

        backend.insert(
            titile=title,
            value=value,
            constant=constant,
            comment=comment,
            workspace=workspace_manager.current_workspace,
        )
        self._sync_after_write()
        self.title_input.text = ""
        self.value_input.text = ""
        self.constant_input.text = ""
        self.comment_input.text = ""
        self.refresh_list()
        self.log(f"Added: {title}")

    def bump_value(self, item, step, *_):
        item_id, title, value, constant, comment, _ = self._unpack_item(item)
        constant_lower = str(constant).lower().strip()

        try:
            if constant_lower == "episodes":
                episode_map = json.loads(value) if value else {}
                if not episode_map:
                    episode_map = {"1": [1]}
                last_season = str(max(int(season) for season in episode_map.keys()))
                last_episode = max(episode_map[last_season])
                new_episode = last_episode + step
                if new_episode < 1:
                    self.log("Episode cannot be less than 1.")
                    return
                episode_map[last_season].append(new_episode)
                new_value = json.dumps(episode_map)
            else:
                new_value = int(value) + step

            backend.update(
                item_id,
                title=title,
                value=new_value,
                constant=constant,
                comment=comment,
                workspace=workspace_manager.current_workspace,
            )
            self._sync_after_write()
            self.refresh_list()
            self.log(f"Updated: {title}")
        except Exception as exc:
            self.log(f"Update failed: {exc}")

    def delete_item(self, item_id, *_):
        try:
            backend.delete(item_id, workspace=workspace_manager.current_workspace)
            self._sync_after_write()
            self.refresh_list()
            self.log(f"Deleted item #{item_id}")
        except Exception as exc:
            self.log(f"Delete failed: {exc}")

    def open_edit_popup(self, item, *_):
        item_id, title, value, constant, comment, sessions = self._unpack_item(item)
        parsed_sessions = None
        if sessions:
            try:
                parsed_sessions = json.loads(sessions)
            except (TypeError, json.JSONDecodeError):
                parsed_sessions = None

        pop_root = Card(THEME["panel"], orientation="vertical", padding=dp(10), spacing=dp(8))
        form = GridLayout(cols=2, spacing=dp(8), size_hint_y=0.8)
        title_input = ThemedInput(text=str(title))
        value_input = ThemedInput(text=str(value))
        constant_input = ThemedInput(text=str(constant))
        comment_input = ThemedInput(text=str(comment))

        for key in ("Title", "Value", "Constant", "Comment"):
            lbl = Label(text=key, color=THEME["muted"], halign="left", valign="middle")
            lbl.bind(size=self._label_size)
            form.add_widget(lbl)
            if key == "Title":
                form.add_widget(title_input)
            elif key == "Value":
                form.add_widget(value_input)
            elif key == "Constant":
                form.add_widget(constant_input)
            else:
                form.add_widget(comment_input)

        action_row = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(8))
        save_btn = ThemedButton(text="Save", bg=THEME["accent"])
        cancel_btn = ThemedButton(text="Cancel", bg=(0.23, 0.3, 0.42, 1))
        action_row.add_widget(save_btn)
        action_row.add_widget(cancel_btn)

        pop_root.add_widget(form)
        pop_root.add_widget(action_row)

        popup = Popup(
            title=f"Edit Item #{item_id}",
            title_color=THEME["text"],
            separator_color=THEME["accent"],
            content=pop_root,
            size_hint=(0.95, 0.75),
            background_color=(0.02, 0.03, 0.06, 0.92),
        )

        def save_changes(*_):
            try:
                new_value = value_input.text
                if new_value.isdigit():
                    new_value = int(new_value)
                backend.update(
                    item_id,
                    title=title_input.text.strip(),
                    value=new_value,
                    constant=constant_input.text.strip(),
                    comment=comment_input.text.strip(),
                    workspace=workspace_manager.current_workspace,
                    sessions=parsed_sessions,
                )
                self._sync_after_write()
                popup.dismiss()
                self.refresh_list()
                self.log(f"Saved item #{item_id}")
            except Exception as exc:
                self.log(f"Save failed: {exc}")

        save_btn.bind(on_press=save_changes)
        cancel_btn.bind(on_press=lambda *_: popup.dismiss())
        popup.open()


class LofApp(App):
    def build(self):
        if platform == "linux":
            Window.minimum_width = 940
            Window.minimum_height = 640
        start_vlc_tracker_if_available()
        return LofRoot()


if __name__ == "__main__":
    LofApp().run()
