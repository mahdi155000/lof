from plugin import plugin, register_command
from Asset import backend
from workspace_manager_module import workspace_manager


# @register_command("search", 'value')
@register_command("search", 'value')
def search_database():
    """
    Searches the database for entries that match the given query.

    Args:
        query (str): The search query string.

    Returns:
        list: A list of database entries that match the query.
    """
    query = input("Enter search query: ")
    workspace = workspace_manager.current_workspace
    results = backend.search(title=query,value="*", constant="*", comment="*", workspace=workspace)  # Only searching by title
    
    if results:
        for row in results:
            print(" , ".join(map(str, row)))
    else:
        print("No results found.")

    return results

@register_command("search", 'comment')
def search_database():
    """
    Searches the database for entries that match the given query.

    Args:
        query (str): The search query string.

    Returns:
        list: A list of database entries that match the query.
    """
    query = input("Enter search query: ")
    workspace = workspace_manager.current_workspace
    results = backend.search(title="*",value="*", constant="*", comment=query, workspace=workspace)  # Only searching by title
    
    if results:
        for row in results:
            print(" , ".join(map(str, row)))
    else:
        print("No results found.")

    return results
