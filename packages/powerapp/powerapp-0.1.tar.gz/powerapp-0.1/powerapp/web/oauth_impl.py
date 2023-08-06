# -*- coding: utf-8 -*-
from bottle import response, abort

from .oauth import register_oauth_client
from powerapp.config import config
from powerapp.models.todoist_users import TodoistUser
from powerapp.exceptions import AppContainerError


@register_oauth_client('todoist',
                       authorize_endpoint='%s/oauth/authorize' % config.API_ENDPOINT,
                       access_token_endpoint='%s/oauth/access_token' % config.API_ENDPOINT,
                       scope='data:read_write,data:delete,project:delete')
def todoist_oauth(client, access_token):
    try:
        user = TodoistUser.register(access_token)
    except AppContainerError:
        abort(403)
    client.save_access_token(user, access_token)
    response.set_cookie("uid", user.id, secret=config.COOKIE_SECRET,
                        httponly=True, max_age=60*24*365, path='/')
