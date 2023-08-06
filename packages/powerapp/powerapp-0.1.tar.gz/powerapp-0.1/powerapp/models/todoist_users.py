# -*- coding: utf-8 -*-
import datetime
import logging
from copy import deepcopy

import peewee

from powerapp.database import AbstractModel
from powerapp.database_utils import PickleField
from powerapp.exceptions import return_or_raise
import todoist
from powerapp.utils import AttrDict, recursive_attrdict, get_ts
from powerapp.config import config


logger = logging.getLogger(__name__)


class TodoistUser(AbstractModel):
    """
    A class representing Todoist User
    """
    id = peewee.IntegerField(primary_key=True)
    email = peewee.CharField(index=True, unique=True)
    token = peewee.CharField(index=True, null=True)
    api_state = PickleField(null=True)
    next_sync = peewee.IntegerField(default=0, index=True)

    def __repr__(self):
        return '<TodoistUser(%s)>' % self.email

    @classmethod
    def register(cls, api_token=None, email=None, password=None):
        """
        Register new user by API token, email or password.

        We don't re-register a user if it's already stored,  but return a
        previously stored user instead.

        This function can safely be used as a login/signup facility, as it checks
        the validity of credentials. If credentials are not valid, the function
        raises AppContainerError()
        """
        if not api_token and not email:
            raise RuntimeError('Either api_token or email has to be defined')

        if api_token:
            api = todoist.TodoistAPI(api_token, api_endpoint=config.API_ENDPOINT)
        else:
            api = todoist.TodoistAPI(api_endpoint=config.API_ENDPOINT)
            return_or_raise(api.login(email, password))

        return_or_raise(api.user.sync())

        try:
            user = TodoistUser.get(id=api.user.get_id())
        except TodoistUser.DoesNotExist:
            user = TodoistUser.create(
                id=api.user.get_id(),
                email=api.user.get()['email'],
                api_state=api.serialize(),
                token=api.user.get()['token']
            )
        if api_token and user.token != api_token:
            user.token = api_token
            user.save()
        return user

    def cron_sync(self):
        """
        Cron Sync
        """
        logger.debug('Start cron sync for %s' % self.email)
        events = self.sync()
        for integration in self.integrations:
            integration.fire_events(events)

    def get_next_sync(self):
        if self.next_sync:
            return datetime.datetime.utcfromtimestamp(self.next_sync)

    def sync(self):
        """
        Synchronize user data with the server and returns the list
        of signals to emit.

        Every signal is a `TodoistEvent` instance with attributes:
        - name (signal name)
        - args (list of arguments to be passed to signal handler
        - kwargs (dict of kwargs be passed to signal handler)

        Currently all signals are fired with (todoist_user, modified_object)
        args and may have following names:

        - todoist_project_added
        - todoist_project_updated
        - todoist_project_deleted
        - todoist_task_added
        - todoist_task_updated
        - todoist_task_deleted
        - todoist_note_added
        - todoist_note_updated
        - todoist_note_deleted
        """
        api_client = self.get_api_client()
        current_api_state = deepcopy(api_client.state)
        sync_result = recursive_attrdict(api_client.sync(resource_types=['projects', 'items', 'notes']))
        self.save_api_client()
        return list(self.process_sync_result(current_api_state, sync_result))

    def process_sync_result(self, api_state, result):
        """
        Process sync result and yield events, one by one
        """
        _exists_cache = {}
        def exists(state_key, obj_id):
            if state_key not in _exists_cache:
                _exists_cache[state_key] = {obj['id'] for obj in
                                            api_state[state_key]}
            return obj_id in _exists_cache[state_key]

        result_event_map = [
            ('Items', 'task'),
            ('Notes', 'note'),
            ('Projects', 'project'),
        ]

        for result_key, event_type in result_event_map:
            for el in result.get(result_key) or []:
                if el.is_deleted:
                    event_name = 'todoist_%s_deleted' % event_type
                elif exists(result_key, el.id):
                    event_name = 'todoist_%s_updated' % event_type
                else:
                    event_name = 'todoist_%s_added' % event_type

                logger.debug('Fire %s(%r, %r)' % (event_name, self.email,
                                                  el.id))
                yield TodoistEvent(name=event_name, args=[self, el])

    def get_api_client(self):
        """
        Return synchronized (but probably outdated) TodoistAPI client

        :rtype: todoist.TodoistAPI
        """
        if not hasattr(self, '_api_client'):
            if self.api_state:
                api_client = todoist.TodoistAPI.deserialize(self.api_state)
            else:
                api_client = todoist.TodoistAPI(self.token)
            api_client.api_endpoint = config.API_ENDPOINT
            self._api_client = api_client
        return self._api_client

    def save_api_client(self):
        """
        Save Todoist API client state in the store
        """
        self.api_state = self.get_api_client().serialize()
        self.save()

    def get_settings(self, key):
        """
        Return a Todoist user setting
        """
        return self.get_api_client().user.get(key)

    #--- todoist-related functionality

    def add_note(self, item_id, content):
        """
        Add a new note note to the task
        """
        logger.debug('Add note %r', content)
        api = self.get_api_client()
        api.notes.add(item_id, content=content)
        api.commit()
        self.save_api_client()

    def add_task(self, project_id, content, notes=None):
        """
        Add a new task and optionally a list of notes to it
        """
        logger.debug('Add task %r', content)
        api = self.get_api_client()
        item = api.items.add(content, project_id)
        for note in (notes or []):
            api.notes.add(item['id'], note)
        api.commit()
        self.save_api_client()


class TodoistEvent(AttrDict):
    pass


def cron_sync(sync_interval=300):
    """
    Find all users who weren't recently updated, and update them all,
    one by one.

    :param check_interval: the Sync interval (in seconds)
    """
    # TODO: we might perform sync operations in parallel
    now = get_ts()
    next_sync = now + sync_interval
    for user in TodoistUser.select().where(TodoistUser.next_sync < now):
        user.cron_sync()
        user.next_sync = next_sync
        user.save()
