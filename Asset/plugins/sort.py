from plugin import plugin
from Asset import backend

@plugin("sort")
def sort():
    backend.fill_list(backend.view())
    M_L = backend.view()
    counter = 1
    for item in M_L:
        # backend.update(counter, item[1], item[2], item[3], item[4])
        backend.update_id(item[0], counter)
        # item[0] = counter
        counter += 1