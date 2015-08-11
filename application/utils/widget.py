import inspect

widgets = {}


def widget(name):
    def decorator(callback):
        widgets[name] = callback
    return decorator


def get(name, data=None, wrap=False):
    if name in widgets:
        fn = widgets[name]
        specs = inspect.getargspec(fn)
        defaults = specs.defaults or ()
        func_args = zip(specs.args, [None]*(len(specs.args)-len(defaults))+list(defaults))
        fn_data = {}
        for arg, default in func_args:
            if arg is 'data' and len(func_args) == 1:
                fn_data[arg] = data
            else:
                if isinstance(data, dict):
                    if arg in data:
                        fn_data[arg] = data.get(arg, default)
                        del data[arg]
                elif isinstance(data, list):
                    fn_data[arg] = data.pop(0)
                else:
                    fn_data[arg] = data or default
                    data = None
        if isinstance(data, dict) and specs.keywords:
            fn_data = dict(data.items()+fn_data.items())


        if len(list(func_args)) == 0:
            return str(fn()) if wrap else str(fn())
        else:
            return str(fn(**fn_data)) if wrap else str(fn(**fn_data))
    return ""

__all__ = ["widget", "get"]