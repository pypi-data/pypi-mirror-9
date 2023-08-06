# -*- coding: utf-8 -*-
import re
import os
import six
from importlib import import_module
from powerapp.utils import AttrDict


CONFIG_VARIABLE = re.compile(r'^[A-Z0-9_]+$')


class Config(AttrDict):

    def load_module(self, module_name):
        module = import_module(module_name)
        ret = {}
        for key in dir(module):
            if CONFIG_VARIABLE.match(key):
                ret[key] = getattr(module, key)

        self.update(ret)

    def load_python(self, filename):
        if os.path.isfile(filename):
            d = dict(self.__dict__)
            six.exec_(open(filename).read(), d)
            self.update({k: v for k, v in d.items() if CONFIG_VARIABLE.match(k)})

    def load_environ(self):
        self.update({k: v for k, v in os.environ.items() if CONFIG_VARIABLE.match(k)})

#: global configuration object. Initialized by `init.init()` function
config = Config()
