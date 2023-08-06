# -*- coding: utf-8 -*-
import datetime
import logging

import peewee

from powerapp.database import db, AbstractModel
from powerapp.models.integrations import Integration
from powerapp.models.todoist_users import TodoistUser
from powerapp.utils import get_ts


logger = logging.getLogger(__name__)


class IntegrationPeriodicTask(AbstractModel):
    """
    Integration is a connector between service and todoist user. It stores
    the fact that user "foo" wants to receive notifications from the service
    "bar" and also contains all the settings for this connection.
    """
    name = peewee.CharField()
    integration = peewee.ForeignKeyField(Integration, index=True, related_name='periodic_tasks')
    service_id = peewee.CharField(index=True)
    user = peewee.ForeignKeyField(TodoistUser, index=True, related_name='integration_periodic_tasks')
    next_run = peewee.IntegerField(default=True, index=True)

    def get_service(self):
        from powerapp import services
        return services.get_by_id(self.service_id)

    def run(self):
        # 1. find itself in a service
        service = self.get_service()
        try:
            func, interval = service.periodic_tasks[self.name]
        except KeyError:
            # unknown periodic task, will be destroyed upon next sync operation
            return
        # 2. run the task itself, as being asked
        logger.debug('Run periodic task %r', self.get_name())
        func(self.integration, self.user)
        # 3. update the database
        next_run = get_ts(datetime.datetime.utcnow() + interval)
        self.change(next_run=next_run)

    def get_next_run(self):
        if self.next_run:
            return datetime.datetime.utcfromtimestamp(self.next_run)

    def get_name(self):
        return '%s-%s' % (self.name, self.integration.get_name())


def sync(integration):
    """
    Fill in the table of periodic tasks.

    1. Add periodic tasks known to current integration
    2. Delete "outdated" (unknown to current integration) periodic tasks
    """
    service = integration.get_service()
    if not service.periodic_tasks:
        return

    known_tasks = IntegrationPeriodicTask.select().where(
        IntegrationPeriodicTask.integration == integration
    )

    # collect all periodic tasks to delete
    to_delete = []
    for task in known_tasks:
        if task.name not in service.periodic_tasks:
            to_delete.append(task.id)

    # collect all periodic tasks to create
    to_add = []
    known_task_names = {t.name for t in known_tasks}
    for task_name in service.periodic_tasks.keys():
        if task_name not in known_task_names:
            to_add.append({'name': task_name,
                           'integration_id': integration.id,
                           'service_id': integration.service_id,
                           'user_id': integration.user.id})

    # perform modifications
    with db.transaction():
        if to_delete:
            IntegrationPeriodicTask.delete().where(IntegrationPeriodicTask.id << to_delete)
        if to_add:
            IntegrationPeriodicTask.insert_many(to_add)


def cron_run():
    """
    Find all periodic tasks which have to be executed, and run them
    """
    # TODO: we might want to perform run operations in parallel
    now = get_ts()
    for task in IntegrationPeriodicTask.select().where(IntegrationPeriodicTask.next_run < now):
        task.run()
