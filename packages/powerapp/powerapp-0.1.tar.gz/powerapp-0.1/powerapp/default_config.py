# -*- coding: utf-8 -*-
"""
Default configuration settings
"""
import os

PYTEST_MODE = False
API_ENDPOINT = 'https://api.todoist.com'
DATABASE_ECHO = False
COOKIE_SECRET = ''
APP_CONTAINER_ROOT = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = 'sqlite://%s/powerapp.sqlite' % os.path.dirname(APP_CONTAINER_ROOT)
