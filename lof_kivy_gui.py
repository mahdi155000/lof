#!/usr/bin/env python3
from kivy.app         import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button     import Button
from kivy.uix.label      import Label
from kivy.uix.textinput  import TextInput
from kivy.uix.popup      import Popup
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.properties import ListProperty

from Asset import backend
from workspace_manager_module import workspace_manager

class ItemList(RecycleView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = RecycleBoxLayout(
            default_size=(None, 40),
            default_size_hint=(1, None),
            size_hint=(1, None),
            orientation='vertical'
        )
        layout.bind(minimum_height=layout.setter('height'))
        self.add_widget(layout)
        self.layout_manager = layout

        self.viewclass = 'Label'

    def update_items(self, items):
        self.data = [
            {'text': f"{it[0]} | {it[1]}" ,
             'height': 40, 'size_hint_y': None}
            for it in items
        ]
        self.refresh_from_data()

class LOFRoot(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)

        ws = workspace_manager.current_workspace
        backend.connect(ws)

        h = BoxLayout(size_hint_y=None, height=50)
        h.add_widget(Label(text="Workspace:", size_hint_x=0.2))
        self.ws_input = TextInput(text=ws, multiline=False, size_hint_x=0.4)
        h.add_widget(self.ws_input)
        btn = Button(text="Switch", size_hint_x=0.2)
        btn.bind(on_release=self.switch_workspace)
        h.add_widget(btn)
        self.add_widget(h)

        self.item_list = ItemList(size_hint=(1, 0.8))
        self.add_widget(self.item_list)

        f = BoxLayout(size_hint_y=None, height=60)
        for label, handler in [
            ("Add", self.add_item),
            ("Edit", self.edit_item),
            ("Delete", self.delete_item),
            ("Refresh", self.refresh_list),
        ]:
            b = Button(text=label)
            b.bind(on_release=handler)
            f.add_widget(b)
        self.add_widget(f)

        self.refresh_list()

    def refresh_list(self, *args):
        ws = self.ws_input.text.strip()
        items = backend.view(ws)
        print("VIEW:", items)    # <-- Check this output
        self.item_list.update_items(items)

    def switch_workspace(self, instance):
        newws = self.ws_input.text.strip()
        workspace_manager.switch_workspace(newws)
        backend.connect(newws)
        self.refresh_list()

    def add_item(self, *a): self.show_item_popup("Add")
    def edit_item(self, *a): self.show_info("Not selected")
    def delete_item(self, *a): self.show_info("Not selected")
    def show_item_popup(self, t, it=None, idx=None): self.show_info("popup")
    def show_info(self, msg):
        Popup(title="Info", content=Label(text=msg), size_hint=(0.5, 0.3)).open()

class LOFApp(App):
    def build(self):
        return LOFRoot()

if __name__ == "__main__":
    LOFApp().run()
