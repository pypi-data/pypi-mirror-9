# -*- coding: utf-8 -*-
import wtforms
from bottle import request, redirect, abort

from powerapp.models import integrations
from powerapp.models.integrations import Integration
from powerapp.web.utils import ensure_user
from powerapp.web.web import app
from powerapp.web.utils import render


@app.route('/integrations/rss/add', method=['GET', 'POST'])
def add_integration():
    user = ensure_user()
    form = RSSForm(user, formdata=request.forms)
    if request.method == 'POST' and form.validate():
        integrations.register('rss', user.id,
                              name=form.name.data,
                              feed_url=form.feed_url.data,
                              project_id=form.project.data)
        redirect('/')
    return render('rss/add.mako', user=user, form=form)


@app.route('/integrations/rss/<integration_id:int>/edit', method=['GET', 'POST'])
def edit_integration(integration_id):
    user = ensure_user()
    try:
        obj = Integration.get(id=integration_id, user=user.id)
    except Integration.DoesNotExist:
        abort(404)

    saved = False
    data = {'name': obj.name,
            'feed_url': obj.settings['feed_url'],
            'project': obj.settings['project_id']}
    form = RSSForm(user, formdata=request.forms, data=data)
    if request.method == 'POST' and form.validate():
        obj.name = form.name.data
        obj.update_settings(feed_url=form.feed_url.data,
                            project_id=form.project.data)
        obj.save()
        saved = True
    return render('rss/edit.mako', user=user, form=form, obj=obj, saved=saved)


class RSSForm(wtforms.Form):

    name = wtforms.StringField(
        label='Integration name',
        default='My RSS to Todoist integration',
        validators=[wtforms.validators.required(),
                    wtforms.validators.length(max=256)]
    )
    feed_url = wtforms.StringField(
        label='RSS Feed URL',
        description=u'Here we take the news from',
        validators=[wtforms.validators.URL(),
                    wtforms.validators.required()]
    )
    project = wtforms.SelectField(
        label='Project Name',
        description=u'Here we add RSS items as tasks',
        validators=[wtforms.validators.required()],
        coerce=int)

    def __init__(self, user, *args, **kwargs):
        super(RSSForm, self).__init__(*args, **kwargs)
        api = user.get_api_client()
        api.projects.sync()
        choices = [(p['id'], p['name']) for p in api.projects.all()]
        self.project.choices = choices
        self.project.default = api.user.get('inbox_project')
