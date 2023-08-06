# -*- coding: utf-8 -*-
from bottle import redirect

from powerapp.web.utils import ensure_user
from powerapp.web.web import app
from powerapp.models import integrations


@app.route('/integrations/amazon/add')
def add_integration():
    user = ensure_user()
    integrations.register('amazon', user.id)
    redirect('/')
