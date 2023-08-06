import os
import datetime
from six import text_type, binary_type
from pprint import pformat
from importlib import import_module
import inspect


class AttrDict(dict):
    """
    Dict allowing to get access to its keys as attributes
    """

    def __getattr__(self, name):
        if name in self:
            return self[name]
        raise AttributeError('%s not found' % name)

    def __setattr__(self, name, value):
        self[name] = value

    def __repr__(self):
        formatted_dict = pformat(dict(self))
        classname = self.__class__.__name__
        return '%s(%s)' % (classname, formatted_dict)

    @property
    def __members__(self):
        return self.keys()



def recursive_attrdict(obj):
    """
    Recursively find all dicts in a stricture, and convert them to attr dict
    """
    if isinstance(obj, (dict, AttrDict)):
        return AttrDict({k: recursive_attrdict(v) for k, v in obj.items()})

    if isinstance(obj, (list, tuple, set)):
        return obj.__class__([recursive_attrdict(item) for item in obj])

    return obj


def recursive_dict(obj):
    """
    Inverse operation: recursively find all AttrDicts in a stricture, and
    convert them to plain dicts
    """
    if isinstance(obj, (dict, AttrDict)):
        return {k: recursive_dict(v) for k, v in obj.items()}

    if isinstance(obj, (list, tuple, set)):
        return obj.__class__([recursive_dict(item) for item in obj])

    return obj


def get_object(python_path):
    """
    Get object by its full "module path"
    """
    module_name, object_name = python_path.rsplit('.', 1)
    module = import_module(module_name)
    return getattr(module, object_name)



def scan_package_for_instances(module_name_or_instance, base_class):
    object_matcher = lambda obj: isinstance(obj, base_class)
    return scan_package_for_objects(module_name_or_instance, object_matcher)


def scan_package_for_subclasses(module_name_or_instance, base_class):

    def object_matcher(obj):
        if not isinstance(obj, type):
            return False
        return issubclass(obj, base_class)

    ret = scan_package_for_objects(module_name_or_instance, object_matcher)
    ret = list(set(ret))
    return ret


def scan_package_for_objects(module_name_or_instance, object_matcher):
    """
    Scan package and all first-level subpackages for objects of a certain
    kind.

    `object_matcher` is a function accepting an object and returning True or False

    For example, there is a structure::


        app/module/__init__.py
                  foo.py
                  bar.py

    We may ask for something like::

        scan_package_for_objects("app.module", lambda obj: isinstance(obj, basestring))

    and it finds all globally defined strings
    """
    if isinstance(module_name_or_instance, (text_type, binary_type)):
        module_name = module_name_or_instance
        pkg = import_module(module_name_or_instance)
    else:
        module_name = module_name_or_instance.__name__
        pkg = module_name_or_instance

    ret = []
    ret += [m for _, m in inspect.getmembers(pkg, object_matcher)]

    pkg_filename = pkg.__file__
    pkg_basename, _ = os.path.splitext(os.path.basename(pkg_filename))
    if pkg_basename != '__init__':
        return ret

    pkg_dir = os.path.dirname(pkg_filename)
    for filename in sorted(os.listdir(pkg_dir)):
        basename, ext = os.path.splitext(filename)
        if basename == '__init__' or ext != '.py':
            continue

        mod = import_module('%s.%s' % (module_name, basename))
        ret += [m for _, m in inspect.getmembers(mod, object_matcher)]

    return ret


def get_ts(dt=None, epoch=datetime.datetime(1970, 1, 1)):
    """
    Convert UTC datetime to timestamp

    Usage example::

        >>> get_ts(datetime.datetime.utcnow())
    """
    if dt is None:
        dt = datetime.datetime.utcnow()
    return int((dt - epoch).total_seconds())
