# -*- coding: utf-8 -*-
import os

from six.moves.urllib import parse
from six import text_type
from bottle import request, redirect
from mako.lookup import TemplateLookup

from powerapp.config import config
from powerapp import services
from powerapp.models.todoist_users import TodoistUser


web_root = os.path.dirname(__file__)
_lookup = None


cookie_not_set = RuntimeError('config.COOKIE_SECRET is not set. Set it up in '
                              'your powerapp.cfg.py file')


def ensure_user():
    user = get_user()
    if not user:
        redirect(extend_qs('/login', url=request.path))
    return user


def get_user():
    if not config.COOKIE_SECRET:
        raise cookie_not_set
    uid = request.get_cookie("uid", secret=config.COOKIE_SECRET)
    if not uid:
        return None
    return TodoistUser.select().where(TodoistUser.id == uid).first()


def get_redirect_url(default='/'):
    url = request.params.get('url')
    if not url:
        return default

    parsed_url = parse.urlparse(url)
    if parsed_url.scheme or parsed_url.netloc:
        return default

    return url


def get_absolute_url(url):
    """
    convert relative URL to absolute one
    """
    url_chunks = parse.urlsplit(url)
    chunks = list(request.urlparts)
    chunks[2:5] = url_chunks[2:5]
    return parse.urlunsplit(chunks)


def extend_qs(base_url, **kwargs):
    """
    Extend querystring of the URL with kwargs, taking care of python types.

    - True is converted to "1"
    - When a value is equal to False or None, then corresponding key is removed
      from the querystring at all. Please note that empty strings and numeric
      zeroes are not equal to False here.
    - Unicode is converted to utf-8 string
    - Everything else is converted to string using str(obj)

    For instance:

    >>> extend_querystring('/foo/?a=b', c='d', e=True, f=False)
    '/foo/?a=b&c=d&e=1'
    """
    parsed = parse.urlparse(base_url)
    query = dict(parse.parse_qsl(parsed.query))
    for key, value in kwargs.items():
        value = convert_to_string(value)
        if value is None:
            query.pop(key, None)
        else:
            query[key] = value
    query_str = parse.urlencode(query)
    parsed_as_list = list(parsed)
    parsed_as_list[4] = query_str
    return parse.urlunparse(parsed_as_list)


def convert_to_string(value):
    """
    Helper function converting python objects to strings

    None is special value menaning "remove me from the queryset"
    """
    if value is None or value is False:
        return None
    if value is True:
        return '1'
    if isinstance(value, text_type):
        return value.encode('utf-8')
    return str(value)


def get_lookup():
    """
    Return a template lookup searching across all application templates
    """
    global _lookup
    if _lookup is None:
        templates = lambda d: os.path.join(d, 'templates')
        directories = [templates(web_root)]
        directories += [templates(s.root) for s in services.get_all().values()]
        _lookup = TemplateLookup(directories)
    return _lookup


def render(template_name, **kwargs):
    return get_lookup().get_template(template_name).render(**kwargs)
