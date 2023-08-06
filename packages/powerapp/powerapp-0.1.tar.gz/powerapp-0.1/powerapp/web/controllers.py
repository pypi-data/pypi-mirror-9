# -*- coding: utf-8 -*-
import os

from bottle import redirect, request, response, abort, static_file

from powerapp.config import config
from powerapp import services
from powerapp.models.integrations import Integration
from powerapp.web.web import app
from powerapp.web import oauth
from powerapp.web.utils import ensure_user, get_user, get_redirect_url, render


@app.route('/')
def dashboard():
    user = ensure_user()
    service_list = services.get_all()
    integration_list = Integration.select().where(Integration.user == user.id)
    return render('/dashboard.mako', user=user,
                  active='dashboard',
                  service_list=service_list.values(),
                  integration_list=integration_list)


@app.route('/services')
def services_list():
    user = ensure_user()
    service_list = services.get_all()
    return render('/services.mako', user=user,
                  active='services',
                  service_list=service_list.values())


@app.route('/login')
def login():
    user = get_user()
    if user:
        redirect(get_redirect_url())

    client = oauth.get_client_by_name('todoist')
    authorize_url = client.get_authorize_url()
    return render('/login.mako', authorize_url=authorize_url)


@app.route('/logout')
def logout():
    response.delete_cookie('uid')
    redirect('/')


@app.route('/oauth2cb')
def oauth2cb():
    if 'error' in request.query:
        return render('/oauth2cb.mako', error=request.query['error'])
    code = request.query.get('code')
    state = request.query.get('state')
    client = oauth.get_client_by_state(state)
    access_token = client.exchange_code_for_token(code)
    client.callback_fn(client, access_token)
    redirect(get_redirect_url(client.oauth2cb_redirect_uri))


@app.route('/integrations/<service_id>/<integration_id:int>/delete')
def delete_integration(service_id, integration_id):
    # FIXME! CSRF protection
    user = ensure_user()
    try:
        obj = Integration.get(id=integration_id, user=user)
    except Integration.DoesNotExist:
        abort(404)
    obj.delete_instance()
    redirect('/')


@app.route('/static/common/<filepath:path>')
def common_static(filepath):
    root = os.path.join(config.APP_CONTAINER_ROOT, 'web/static')
    return static_file(filepath, root=root)
