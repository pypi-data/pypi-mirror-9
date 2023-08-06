# -*- coding: utf-8 -*-
from powerapp.services import Service
import re
import time
import datetime
import logging
import requests
import feedparser

s = Service(name='RSS Feed handler')


@s.periodic_task(datetime.timedelta(seconds=10))
def handle_rss_feed(integration, todoist_user):
    """
    :param powerapp.integrations.Integration integration: a
    :param powerapp.todoist_users.TodoistUser todoist_user: a
    :return:
    """

    feed_url = integration.settings.get('feed_url')
    last_updated = integration.settings.get('last_updated', 0)
    project_id = integration.settings.get('project_id', todoist_user.get_settings('inbox_project'))

    if not feed_url:
        logging.error('Integration %s does not have a "feed_url" attribute',
                      integration.get_name())
        return
    resp = requests.get(feed_url).content
    feed = feedparser.parse(resp)

    published_dates = [last_updated]
    known_urls = get_urls(todoist_user, project_id)

    for entry in feed.entries:
        # filter out by last update
        if 'published_parsed' in entry:
            published = int(time.mktime(entry.published_parsed))
            published_dates.append(published)
            if published < last_updated:
                continue

        # filter out by currently known records
        if entry.link in known_urls:
            continue

        content = u'%s (%s)' % (entry.link, entry.title)
        todoist_user.add_task(project_id, content=content)

    if max(published_dates) > last_updated:
        integration.update_settings(last_updated=max(published_dates))

re_url = re.compile(r'https?://[^ \(\)]+')


def get_urls(todoist_user, project_id):
    api_client = todoist_user.get_api_client()
    urls = set()
    items = api_client.items.all(lambda i: i['project_id'] == project_id)
    for item in items:
        urls.update(re_url.findall(item['content']))
    return urls
