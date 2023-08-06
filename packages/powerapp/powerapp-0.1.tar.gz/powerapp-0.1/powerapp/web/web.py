# -*- coding: utf-8 -*-
from bottle import Bottle, load
from powerapp import services

app = Bottle()
load('powerapp.web.controllers')

for service in services.get_all().values():
    # load service controllers
    service.load_module('controllers')
    # load service static
    app.route('/static/%s/<filepath:path>' % service.id)(service.serve_static)
