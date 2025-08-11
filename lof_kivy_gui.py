#!/usr/bin/env python3
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.properties import ListProperty, NumericProperty, StringProperty
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior

from Asset import backend
from workspace_manager_module import workspace_manager


class SelectableLabel(RecycleDataViewBehavior, Label):
    ''' Add selection support to labels in RecycleView '''
    index = NumericProperty(0)
    selected = False
    selectable = True

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        return super().refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        if super().on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            # Notify parent RV to select this index
            self.parent.parent.selected_index = self.index
            self.parent.select_with_touch(self.index, touch)
            return True

    def apply_selection(self, rv, index, is_selected):
        self.selected = is_selected
        self.canvas.ask_update()
        if is_selected:
            self.color = (1, 1, 1, 1)
            self.canvas.before.clear()
            with self.canvas.before:
                from kivy.graphics import Color, Rectangle
                Color(0.2, 0.5, 0.9, 0.5)
                self.rect = Rectangle(pos=self.pos, size=self.size)
            self.bind(pos=self.update_rect, size=self.update_rect)
        else:
            self.color = (1, 1, 1, 1)
            self.canvas.before.clear()

    def update_rect(self, *args):
        if hasattr(self, 'rect'):
            self.rect.pos = self.pos
            self.rect.size = self.size


class ItemList(RecycleView):
    selected_index = NumericProperty(-1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.viewclass = 'SelectableLabel'

        layout = RecycleBoxLayout(
            default_size=(None, 40),
            default_size_hint=(1, None),
            size_hint=(1, None),
            orientation='vertical',
            spacing=2
        )
        layout.bind(minimum_height=layout.setter('height'))
        self.layout_manager = layout

    def update_items(self, items):
        self.data = [{'text': f"{it[0]} | {it[1]}", 'index': idx} for idx, it in enumerate(items)]
        self.selected_index = -1


class LOFRoot(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=10, spacing=10, **kwargs)

        self.current_items = []
        self.selected_index = -1

        ws = workspace_manager.current_workspace
        backend.connect(ws)

        # Workspace selector
        ws_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        ws_layout.add_widget(Label(text="Workspace:", size_hint_x=0.2))
        self.ws_input = TextInput(text=ws, multiline=False, size_hint_x=0.5)
        ws_layout.add_widget(self.ws_input)
        switch_btn = Button(text="Switch", size_hint_x=0.3)
        switch_btn.bind(on_release=self.switch_workspace)
        ws_layout.add_widget(switch_btn)
        self.add_widget(ws_layout)

        # Item list
        self.item_list = ItemList(size_hint=(1, 0.75))
        self.item_list.bind(selected_index=self.on_item_selected)
        self.add_widget(self.item_list)

        # Action buttons
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        for label, handler in [
            ("Add", self.add_item),
            ("Edit", self.edit_item),
            ("Delete", self.delete_item),
            ("Refresh", self.refresh_list),
        ]:
            btn = Button(text=label)
            btn.bind(on_release=handler)
            btn_layout.add_widget(btn)
        self.add_widget(btn_layout)

        self.refresh_list()

    def on_item_selected(self, instance, value):
        self.selected_index = value

    def refresh_list(self, *args):
        ws = self.ws_input.text.strip()
        self.current_items = backend.view(ws)
        self.item_list.update_items(self.current_items)

    def switch_workspace(self, *args):
        new_ws = self.ws_input.text.strip()
        workspace_manager.switch_workspace(new_ws)
        backend.connect(new_ws)
        self.refresh_list()

    def add_item(self, *args):
        self.show_item_popup("Add")

    def edit_item(self, *args):
        if self.selected_index == -1:
            self.show_info("Please select an item to edit.")
        else:
            item = self.current_items[self.selected_index]
            self.show_item_popup("Edit", item, self.selected_index)

    def delete_item(self, *args):
        if self.selected_index == -1:
            self.show_info("Please select an item to delete.")
        else:
            item = self.current_items[self.selected_index]
            backend.delete(item[0])  # Assuming first element is ID/key
            self.refresh_list()

    def show_item_popup(self, mode, item=None, idx=None):
        box = BoxLayout(orientation='vertical', spacing=10, padding=10)
        input_label = Label(text="Item Text:")
        item_input = TextInput(multiline=False)

        if item:
            item_input.text = item[1]  # Assuming second element is display text

        box.add_widget(input_label)
        box.add_widget(item_input)

        btn_box = BoxLayout(size_hint_y=None, height=40, spacing=10)
        ok_btn = Button(text="OK")
        cancel_btn = Button(text="Cancel")
        btn_box.add_widget(ok_btn)
        btn_box.add_widget(cancel_btn)
        box.add_widget(btn_box)

        popup = Popup(title=f"{mode} Item", content=box, size_hint=(0.5, 0.4), auto_dismiss=False)

        def on_ok(instance):
            new_text = item_input.text.strip()
            if not new_text:
                self.show_info("Input cannot be empty.")
                return
            ws = self.ws_input.text.strip()
            if mode == "Add":
                backend.add(new_text, ws)
            elif mode == "Edit" and idx is not None:
                backend.edit(self.current_items[idx][0], new_text, ws)  # Assuming key is first element
            popup.dismiss()
            self.refresh_list()

        def on_cancel(instance):
            popup.dismiss()

        ok_btn.bind(on_release=on_ok)
        cancel_btn.bind(on_release=on_cancel)

        popup.open()

    def show_info(self, message):
        Popup(title="Info", content=Label(text=message), size_hint=(0.5, 0.3)).open()


class LOFApp(App):
    def build(self):
        return LOFRoot()


if __name__ == "__main__":
    LOFApp().run()
