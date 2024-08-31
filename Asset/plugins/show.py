from plugin import plugin
from Asset import backend
import termcolor2

M_L = []
# This is for now I'll we fix this repeat lately
def fill_list(loff):
    for work in loff:
        M_L.insert(10000, work)

@plugin("show")
def show_function(do_what='plus'):
    fill_list(backend.view())
    M_L= backend.view()
    id_counter = 1
    for item in M_L:
        if item[0] % 2:
            show_color = 'blue'
        else:
            show_color = 'red'
        if item[0] < 10:
            text = (" {:<1}) for {} one {:<45} {}".format(id_counter, do_what, item[1], item[2]))
        else:
            text = ("{:<1}) for {} one {:<45} {}".format(id_counter, do_what, item[1], item[2]))
        print(termcolor2.colored(text, show_color))
        id_counter += 1
