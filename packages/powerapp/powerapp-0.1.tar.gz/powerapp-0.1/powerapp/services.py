# -*- coding: utf-8 -*-
import os
import glob
import inspect
from importlib import import_module

from bottle import static_file
import pkg_resources

from powerapp.models import integrations
from powerapp.models.integrations import Integration
from powerapp.utils import scan_package_for_subclasses, \
    scan_package_for_instances


_services_cache = None


class Service(object):
    """
    Service is a "wrapper" and enumerator for services defined in the
    `services_impl` module.

    The service is initialized with the `root` parameter, which can be a
    filename or a module directory, and optional `id` and `name` attributes
    """

    def __init__(self, id=None, name=None, package_name=None, root=None,
                 logo_filename=None):
        caller_frame, caller_root, _, _, _, _ = inspect.stack()[1]
        if package_name is None:
            module_name = caller_frame.f_globals['__name__']
            package_name, _ = module_name.rsplit('.', 1)

        if root is None:
            root = caller_root
        if os.path.isfile(root):
            root = os.path.dirname(root)
        if id is None:
            id = os.path.basename(root)
        if name is None:
            name = id.title()

        self.id = id
        self.name = name
        self.root = root
        self.package_name = package_name
        self.event_handlers = {}
        self.periodic_tasks = {}
        self.detect_logo_filename(logo_filename)

    def detect_logo_filename(self, logo_filename):
        if not logo_filename:
            static_root = os.path.join(self.root, 'static')
            choices = glob.glob1(static_root, 'logo.*')
            if choices:
                logo_filename = choices[0]
        self.logo_filename = logo_filename

    def get_logo_path(self):
        if self.logo_filename:
            return '/static/%s/%s' % (self.id, self.logo_filename)
        else:
            return '/static/common/default_logo.png'

    def serve_static(self, filepath):
        return static_file(filepath, root=os.path.join(self.root, 'static'))

    def event_handler(self, event_name):
        """ decorator for registering event handlers.

        Decorated function should accept two arguments
        - todoist_user instance
        - added/modified/deleted object

        See `TodoistUser.sync` docstring for all currently available event types
        """
        def decorator(func):
            self.event_handlers[event_name] = func
            return func
        return decorator

    def periodic_task(self, timedelta):
        """ decorator for registering periodic tasks """
        def decorator(func):
            # we use dict instead of list to ensure uniqueness
            self.periodic_tasks[func.__name__] = (func, timedelta)
            return func
        return decorator

    def get_integrations(self):
        """
        Return all integrations with current service
        """
        return Integration.select().where(Integration.service_id == self.id)

    def load_module(self, name, quiet=True):
        full_name = '%s.%s' % (self.package_name, name)
        try:
            return import_module(full_name)
        except ImportError:
            if quiet:
                return None
            raise

    def __repr__(self):
        return '<Service: %s>' % self.id


def get_by_id(service_id):
    """
    Return service by its id (the string)
    """
    return get_all().get(service_id)


def get_all():
    """
    Return all known services. Currently it only searches for records in
    `powerapp.services_impl`
    """
    global _services_cache
    if _services_cache is None:
        _services_cache = {}
        _services_cache.update(scan_package_by_services('powerapp.services_impl'))
        _services_cache.update(scan_setuptools_entry_points_by_services())
    return _services_cache


def scan_package_by_services(package_name, service_file='service.py'):
    """
    Scan package and search for all services inside. It is supposed that the
    package with services has following structure:

        <package_root>/<service_name>/service.py
                                     /controllers.py (optional)
                                     /templates/<service_name>/<...>.mako
                                                               <...>.mako
                                     /static/...


    It's also supposed that the `service.py` file has at least one instance of
    `Service`.

    :param package_name: package name (as "foo.bar")
    :param service_file: optional name of the file where we search for Service
        instances
    :return: the list of Service instances
    :rtype: dict[str, Service]
    """
    service_module, _ = os.path.splitext(service_file)
    pkg = import_module(package_name)
    package_dir = os.path.dirname(pkg.__file__)
    ret = {}
    for dirname in os.listdir(package_dir):
        if not os.path.isdir(os.path.join(package_dir, dirname)):
            continue
        service_filename = os.path.join(package_dir, dirname, service_file)
        if not os.path.isfile(service_filename):
            continue
        mod = import_module('%s.%s.%s' % (package_name, dirname, service_module))
        for _, obj in inspect.getmembers(mod, lambda obj: isinstance(obj, Service)):
            ret[obj.id] = obj
    return ret


def scan_setuptools_entry_points_by_services(entry_point_name='powerapp_services'):
    ret = {}
    for ep in pkg_resources.iter_entry_points(entry_point_name):
        pkg = ep.load()
        services = scan_package_for_instances(pkg, Service)
        for obj in services:
            ret[obj.id] = obj
    return ret
