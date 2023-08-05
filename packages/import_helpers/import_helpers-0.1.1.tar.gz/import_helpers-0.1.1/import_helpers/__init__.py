from collections import defaultdict
import inspect
import types
import sys

__author__ = 'mturilin'



def module_attr_for_name(full_attr_name):
    m_name, attr_name = full_attr_name.rsplit(".", 1)
    if m_name:
        module = module_for_name(m_name)
    else:
        module = __package__
    func = getattr(module, attr_name)
    return func


def typed_module_attr_for_name(full_attr_name, type):
    attr = module_attr_for_name(full_attr_name)
    if not isinstance(attr, type):
        raise ImportError("type does not match")
    return attr


def function_for_name(func_name):
    return typed_module_attr_for_name(func_name, types.FunctionType)


def module_for_name(module_name):
    __import__(module_name)
    return sys.modules[module_name]


def class_for_name(class_name):
    attr = module_attr_for_name(class_name)
    if not inspect.isclass(attr):
        raise ImportError(class_name)
    return attr


def class_full_name(cls):
    return cls.__module__ + "." + cls.__name__    


def build_funcmodule_map(datasource_map):
    funcs = defaultdict(dict)
    for ds_name, f_name in datasource_map.iteritems():
        try:
            mod = module_for_name(f_name)
            for func in dir(mod):
                f = mod.__dict__.get(func)
                if isinstance(f, types.FunctionType):
                    funcs[ds_name][func] = f
        except ImportError:
            funcs[ds_name] = function_for_name(f_name)

    return funcs