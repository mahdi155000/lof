from plugin import plugin

# Sample help data
help_data = {
    "show": {
        "description": "Displays items from the list.",
        "usage": "show [item]",
        "examples": [
            "show - Display all items",
            "show item - Display specific item details"
        ],
        "parameters": {
            "item": "Specifies the item to show. If omitted, shows all items."
        }
    },
    # Add more commands here
}

@plugin("help")
def help_function(command=None):
    
    if command is None:
        print("Available commands:")
        for cmd in help_data.keys():
            print(f"- {cmd}")
        print("\nUse 'help [command]' for more details on a specific command.")
    else:
        cmd_help = help_data.get(command)
        if cmd_help:
            print(f"Command: {command}")
            print(f"Description: {cmd_help['description']}")
            print(f"Usage: {cmd_help['usage']}")
            print("Examples:")
            for example in cmd_help['examples']:
                print(f"  {example}")
            print("Parameters:")
            for param, desc in cmd_help['parameters'].items():
                print(f"  {param}: {desc}")
        else:
            print(f"No help available for command '{command}'.")
