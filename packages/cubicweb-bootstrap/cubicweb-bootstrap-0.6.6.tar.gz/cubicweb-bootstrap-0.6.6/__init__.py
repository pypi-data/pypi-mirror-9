"""cubicweb-bootstrap application package


"""

import inspect


def monkeypatch_default_value(func, arg, value):
    # work on the underlying function object if func is a method, that's
    # where 'func_defaults' actually is stored.
    if inspect.ismethod(func):
        func = func.im_func
    argspec = inspect.getargspec(func)
    # ArgSpec.args contains regular and named parameters, only keep the latter
    named_args = argspec.args[-len(argspec.defaults):]
    idx = named_args.index(arg)
    # generate and inject a new 'func_defaults' tuple with the new default value
    new_defaults = func.func_defaults[:idx] + (value,) + func.func_defaults[idx + 1:]
    func.func_defaults = new_defaults
