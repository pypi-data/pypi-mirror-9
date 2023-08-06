# -*- coding: utf-8 -*-
from powerapp.init import init; init()

import bottle
from powerapp.web.web import app


def run():
    bottle.run(app=app, reloader=True)
