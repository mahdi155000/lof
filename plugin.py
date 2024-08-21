plugins = {}

def plugin(name):
    def decorator(func):
        plugins[name] = func
        return func
    return decorator