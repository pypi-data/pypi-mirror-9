import importlib


def settings_from_module(module_string):
    "Returns settings defined in a module as a dictionary."

    module = importlib.import_module(module_string)
    return dict([(i, getattr(module, i)) for i in dir(module) \
                                                        if i[0:2] != '__'])
