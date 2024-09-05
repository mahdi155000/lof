# from Asset.plugins import branch
# plugins = {
#     'branch': {
#         'add': branch.add,
#         'remove': branch.remove,
#         'rename': branch.rename,
#         # سایر زیرشاخه‌ها
#     },
#     # سایر پلاگین‌ها
# }
plugins = {}


def plugin(name):
    def decorator(func):
        plugins[name] = func
        return func
    return decorator


help_registry = {}


def register_help(func):
    help_registry[func.__name__] = func.__doc__.strip(
    ) if func.__doc__ else "No help available."
    return func


def register_command(command, subcommand=None):
    def wrapper(func):
        if command not in plugins:
            plugins[command] = {}
        if subcommand:
            plugins[command][subcommand] = func
        else:
            plugins[command] = func
        return func
    return wrapper
