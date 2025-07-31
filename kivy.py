""" LOF GUI using Kivy - Android Compatible """

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.recycleview import RecycleView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.properties import ListProperty
from Asset import backend
from workspace_manager_module import workspace_manager

class ItemRow(BoxLayout):
    values = ListProperty()

    def __init__(self, values, **kwargs):
        super().__init__(orientation='horizontal', **kwargs)
        self.values = values
        for v in values:
            self.add_widget(Label(text=str(v), size_hint_x=0.2, font_size='18sp'))

class ItemList(RecycleView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = []

    def update_items(self, items):
        self.data = [{'values': item} for item in items]

class LOFRoot(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.workspace = workspace_manager.current_workspace

        # Workspace controls
        ws_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        ws_label = Label(text="Workspace:", size_hint_x=0.2, font_size='18sp')
        self.ws_input = TextInput(text=self.workspace, multiline=False, size_hint_x=0.4, font_size='18sp')
        ws_switch_btn = Button(text="Switch", size_hint_x=0.2, font_size='18sp')
        ws_switch_btn.bind(on_release=self.switch_workspace)
        ws_layout.add_widget(ws_label)
        ws_layout.add_widget(self.ws_input)
        ws_layout.add_widget(ws_switch_btn)
        self.add_widget(ws_layout)

        # Item list in ScrollView for Android
        scroll = ScrollView(size_hint_y=0.7)
        self.item_list = ItemList(size_hint_y=None, height=400)
        scroll.add_widget(self.item_list)
        self.add_widget(scroll)

        # Buttons
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=60)
        add_btn = Button(text="Add", font_size='18sp')
        add_btn.bind(on_release=self.add_item)
        edit_btn = Button(text="Edit", font_size='18sp')
        edit_btn.bind(on_release=self.edit_item)
        delete_btn = Button(text="Delete", font_size='18sp')
        delete_btn.bind(on_release=self.delete_item)
        refresh_btn = Button(text="Refresh", font_size='18sp')
        refresh_btn.bind(on_release=self.refresh_list)
        btn_layout.add_widget(add_btn)
        btn_layout.add_widget(edit_btn)
        btn_layout.add_widget(delete_btn)
        btn_layout.add_widget(refresh_btn)
        self.add_widget(btn_layout)

        self.selected_index = None
        self.refresh_list()

    def refresh_list(self, *args):
        workspace = self.ws_input.text
        items = backend.view(workspace)
        self.item_list.update_items(items)

    def switch_workspace(self, *args):
        new_ws = self.ws_input.text
        workspace_manager.switch_workspace(new_ws)
        backend.connect(new_ws)
        self.refresh_list()

    def add_item(self, *args):
        self.show_item_popup("Add Item")

    def edit_item(self, *args):
        if not self.item_list.data:
            self.show_info("Select an item to edit.")
            return
        index = self.get_selected_index()
        if index is None:
            self.show_info("Select an item to edit.")
            return
        item = self.item_list.data[index]['values']
        self.show_item_popup("Edit Item", item, index)

    def delete_item(self, *args):
        if not self.item_list.data:
            self.show_info("Select an item to delete.")
            return
        index = self.get_selected_index()
        if index is None:
            self.show_info("Select an item to delete.")
            return
        item = self.item_list.data[index]['values']
        popup = Popup(title="Delete", content=Label(text=f"Delete item '{item[1]}'?", font_size='18sp'),
                      size_hint=(0.7, 0.3),
                      auto_dismiss=False)
        btn_yes = Button(text="Yes", font_size='18sp')
        btn_no = Button(text="No", font_size='18sp')
        btn_layout = BoxLayout(orientation='horizontal')
        btn_layout.add_widget(btn_yes)
        btn_layout.add_widget(btn_no)
        popup.content.add_widget(btn_layout)
        def yes_action(instance):
            backend.delete(item[0], workspace=self.ws_input.text)
            self.refresh_list()
            popup.dismiss()
        def no_action(instance):
            popup.dismiss()
        btn_yes.bind(on_release=yes_action)
        btn_no.bind(on_release=no_action)
        popup.open()

    def show_item_popup(self, title, item=None, index=None):
        popup = Popup(title=title, size_hint=(0.9, 0.7))
        layout = GridLayout(cols=2, spacing=10, padding=10)
        title_input = TextInput(text=item[1] if item else "", multiline=False, font_size='18sp')
        value_input = TextInput(text=item[2] if item else "", multiline=False, font_size='18sp')
        constant_input = TextInput(text=item[3] if item else "", multiline=False, font_size='18sp')
        comment_input = TextInput(text=item[4] if item else "", multiline=False, font_size='18sp')
        layout.add_widget(Label(text="Title:", font_size='18sp'))
        layout.add_widget(title_input)
        layout.add_widget(Label(text="Value:", font_size='18sp'))
        layout.add_widget(value_input)
        layout.add_widget(Label(text="Constant:", font_size='18sp'))
        layout.add_widget(constant_input)
        layout.add_widget(Label(text="Comment:", font_size='18sp'))
        layout.add_widget(comment_input)
        btn_ok = Button(text="OK", font_size='18sp')
        btn_cancel = Button(text="Cancel", font_size='18sp')
        btn_layout = BoxLayout(orientation='horizontal')
        btn_layout.add_widget(btn_ok)
        btn_layout.add_widget(btn_cancel)
        layout.add_widget(btn_layout)
        popup.content = layout

        def ok_action(instance):
            title_val = title_input.text
            value_val = value_input.text
            constant_val = constant_input.text
            comment_val = comment_input.text
            if item:
                backend.update(item[0], title_val, value_val, constant_val, comment_val, workspace=self.ws_input.text)
            else:
                backend.insert(title_val, value_val, constant_val, comment_val, workspace=self.ws_input.text)
            self.refresh_list()
            popup.dismiss()
        def cancel_action(instance):
            popup.dismiss()
        btn_ok.bind(on_release=ok_action)
        btn_cancel.bind(on_release=cancel_action)
        popup.open()

    def show_info(self, msg):
        popup = Popup(title="Info", content=Label(text=msg, font_size='18sp'), size_hint=(0.7, 0.3))
        popup.open()

    def get_selected_index(self):
        # Kivy RecycleView does not have built-in selection, so this is a placeholder.
        # You can implement selection by adding a touch event or using a custom view.
        # For now, always return the first item if exists.
        if self.item_list.data:
            return 0
        return None

class LOFApp(App):
    def build(self):
        return LOFRoot()

if __name__ == "__main__":
    LOFApp().run()