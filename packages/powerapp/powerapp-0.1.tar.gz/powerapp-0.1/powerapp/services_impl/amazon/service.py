# -*- coding: utf-8 -*-
from six.moves.urllib.parse import quote
from powerapp.services import Service


s = Service(name='Amazon Search')


@s.event_handler('todoist_task_added')
def add_note_to_task(integration, todoist_user, item):
    if item.content.lower().startswith('buy'):
        target = quote(item.content[4:])
        content = 'http://www.amazon.com/s/?field-keywords=%s (Buy on Amazon)' % target
        todoist_user.add_note(item.id, content=content)
