from plugin import plugin
from Asset import backend
import termcolor2 as tc
from workspace_manager_module import workspace_manager


@plugin("move")
def move_to_other_branch_function():
    try:
        # Input handling for single or multiple columns
        input_items = input(
            f"Enter the {tc.colored('numbers', 'yellow')} of column(s) you want to move (comma-separated for multiple, or single value): ")
        items_to_move = [int(i.strip()) - 1 for i in input_items.split(",")]

        M_L = backend.view(workspace_manager.current_workspace)

        # Show available tables
        print(backend.list_tables())

        # Get destination branch
        destination_branch = input(
            f"Enter new {tc.colored('branch', 'yellow')}: ")

        # Move selected columns
        for item in items_to_move:
            if 0 <= item < len(M_L):  # Check if index is valid
                column = M_L[item]
                backend.move_data(
                    workspace_manager.current_workspace, destination_branch, column[0])
                print(f"Moved column {column[0]} to {destination_branch}")
            else:
                print(f"Invalid column number: {item + 1}")
    except Exception as e:
        print(
            f"An error occurred: {str(e)}. Please try again with valid input.")
