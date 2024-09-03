from plugin import plugin
from Asset import backend
from workspace_manager_module import workspace_manager


@plugin("sort")
def sort():
    backend.fill_list(backend.view(workspace_manager.current_workspace))
    M_L = backend.view(workspace_manager.current_workspace)
    counter = 1
    for item in M_L:
        # backend.update(counter, item[1], item[2], item[3], item[4])
        backend.update_id(item[0], counter,
                          workspace_manager.current_workspace)
        # item[0] = counter
        counter += 1
