from plugin import plugin
from Asset import backend
import termcolor2


@plugin("revalue")
def revalue_function():
    item_you_want_to_revalue = int(input(
        f"Enter {termcolor2.colored('number', 'yellow')} you want to revlaue: ")) - 1
    M_L = backend.view()
    items = M_L[item_you_want_to_revalue]
    x_item = input(f"Enter new {termcolor2.colored('value', 'yellow')}: ")
    backend.update(items[0], items[1], x_item, items[3], items[4])
