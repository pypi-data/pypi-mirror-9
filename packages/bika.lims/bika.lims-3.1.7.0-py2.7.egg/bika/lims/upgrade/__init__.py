# see https://gist.github.com/malthe/704910
import imp
import sys


def create_modules(module_path):
    path = ""
    module = None
    for element in module_path.split('.'):
        path += element

        try:
            module = __import__(path)
        except ImportError:
            new = imp.new_module(path)
            if module is not None:
                setattr(module, element, new)
            module = new

        sys.modules[path] = module
        __import__(path)

        path += "."

    return module


def stub(module_path, class_name, base_class, meta_class=type):
    module = create_modules(module_path)
    cls = meta_class(class_name, (base_class, ), {})
    setattr(module, class_name, cls)
