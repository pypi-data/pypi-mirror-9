# -*- coding: utf-8 -*-
"""
Database object
"""
import peewee
from powerapp.config import config
from powerapp.database_utils import url_to_database
from powerapp.utils import scan_package_for_subclasses

_models = None

db = url_to_database("sqlite://:memory:" if config.PYTEST_MODE else config.DATABASE_URL)


def models(exclude_abstract=True):
    global _models
    if _models is None:
        _models = scan_package_for_subclasses('powerapp.models', peewee.Model)

    if exclude_abstract:
        return list(filter(lambda m: not m.__name__.startswith('Abstract'), _models))
    else:
        return _models


class AbstractModel(peewee.Model):

    class Meta:
        database = db

    def __repr__(self):
        classname = self._meta.model_class.__name__
        return '<%s(%r)>' % (classname, self._data)


def create_all():
    db.create_tables(models(), safe=True)


def drop_all():
    db.drop_tables(models(), safe=True)
