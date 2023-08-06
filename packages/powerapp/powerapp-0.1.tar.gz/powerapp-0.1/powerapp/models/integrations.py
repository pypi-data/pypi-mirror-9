# -*- coding: utf-8 -*-
import time
import datetime
import logging

import peewee

from powerapp.database import AbstractModel
from powerapp.database_utils import PickleField
from powerapp.models.todoist_users import TodoistUser


logger = logging.getLogger(__name__)


class Integration(AbstractModel):
    """
    Integration is a connector between service and todoist user. It stores
    the fact that user "foo" wants to receive notifications from the service
    "bar" and also contains all the settings for this connection.
    """
    name = peewee.CharField(max_length=1024)
    service_id = peewee.CharField(index=True, null=True)
    user = peewee.ForeignKeyField(TodoistUser, related_name='integrations')
    next_sync = peewee.IntegerField(default=0, index=True)
    settings = PickleField(null=True)

    def update_settings(self, **kwargs):
        self.settings = dict(self.settings or {}, **kwargs)
        self.save()

    def get_service(self):
        """
        Return "the service part" of the integration
        """
        from powerapp import services
        return services.get_by_id(self.service_id)

    def fire_events(self, events):
        """
        Accept the list of events and if for some of these events there are
        handlers (one or more), call them
        """
        service = self.get_service()
        for event in events:
            if event.name in service.event_handlers:
                logger.debug('Integration %s. Run handler for "%s" event',
                             self.get_name(), event.name)
                service.event_handlers[event.name](self,
                                                   *event.get('args', []),
                                                   **event.get('kwargs', {}))

    def sync_periodic_tasks(self):
        """
        Fill in the table of periodic tasks.

        1. Add periodic tasks known to current integration
        2. Delete "outdated" (unknown to current integration) periodic tasks
        """
        from ..models.integration_periodic_tasks import IntegrationPeriodicTask
        service = self.get_service()
        if not service.periodic_tasks:
            return

        known_tasks = IntegrationPeriodicTask.select().where(
            IntegrationPeriodicTask.integration == self.id
        )

        to_delete = []
        for task in known_tasks:
            if task.name not in service.periodic_tasks:
                to_delete.append(task.id)


    def run_periodic_tasks(self, check_interval=10):
        """
        Run periodic tasks for the service.

        Every service may register periodic tasks with the
        `periodic_task(timedelta)` decorator. This function starts the infinite
        loop performing these tasks.

        Every periodic task function should accept two arguments:
        - integration instance
        - todoist_user instance
        """
        service = self.get_service()
        if not service.periodic_tasks:
            return

        last_launches = {}
        while True:
            now = datetime.datetime.utcnow()
            for task_name, (func, interval) in service.periodic_tasks.items():
                last_launch = last_launches.get(task_name)
                if not last_launch or now > last_launch + interval:
                    logger.debug('Integration %s. Run periodic task "%s"',
                                 self.get_name(), task_name)
                    func(self, self.get_todoist_user())
                    last_launches[task_name] = now
            time.sleep(check_interval)

    def get_name(self):
        return '%s-%s' % (self.get_service().id,
                          self.user.email)


def register(service_id, user_id, name=None, **settings):
    """
    Register a new integration

    For very service we generate a random id, and in addition to that, the
    caller can provide a dict of settings, connected with this particular
    integration.
    """
    from powerapp.models import integration_periodic_tasks

    if name is None:
        name = '%s integration' % service_id
    obj = Integration.create(service_id=service_id, name=name,
                             user=user_id, settings=settings)
    integration_periodic_tasks.sync(obj)
    return obj
