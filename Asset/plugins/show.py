from plugin import plugin
from Asset import backend
import termcolor2
from workspace_manager_module import workspace_manager


@plugin("show")
def show_function(do_what='plus'):
    M_L = backend.view(workspace_manager.current_workspace)
    id_counter = 1
    for item in M_L:
        if item[0] % 2:
            show_color = 'blue'
        else:
            show_color = 'red'
        if item[0] < 10:
            text = (" {:<1}) for {} one {:<45} {}".format(
                id_counter, do_what, item[1], item[2]))
        else:
            text = ("{:<1}) for {} one {:<45} {}".format(
                id_counter, do_what, item[1], item[2]))
        print(termcolor2.colored(text, show_color))
        id_counter += 1
