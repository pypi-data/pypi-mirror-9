# -*- coding: utf-8 -*-
from importlib import import_module
import os
import logging.config
import peewee
from powerapp.config import config
from powerapp.utils import scan_package_for_subclasses


def init(**config_kwargs):
    """
    Init app container environment
    """
    init_config(**config_kwargs)
    init_logging()
    init_db()
    init_web()


def init_config(**config_kwargs):
    """
    Init configuration
    """
    config.load_module('powerapp.default_config')
    config.load_python(os.environ.get('APP_CONTAINER_CFG', './powerapp.cfg.py'))
    config.load_environ()
    config.update(config_kwargs)


def init_logging():
    """
    Init logging for container environment
    """
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,

        # Formatters
        'formatters': {
            'colored': {
                '()': 'colorlog.ColoredFormatter',
                'format': '%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s',
                'reset': True,
                'log_colors': {
                    'DEBUG':    'cyan',
                    'INFO':     'green',
                    'WARNING':  'yellow',
                    'ERROR':    'red',
                    'CRITICAL': 'red',
                }
            }
        },

        # Handlers
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'colored'
            }
        },

        # Loggers
        'root': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'loggers': {
            'powerapp': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': False,
            }
        }
    })


def init_db():
    from powerapp.database import db, create_all
    db.connect()
    create_all()


def init_web():
    import_module('powerapp.web.oauth_impl')
