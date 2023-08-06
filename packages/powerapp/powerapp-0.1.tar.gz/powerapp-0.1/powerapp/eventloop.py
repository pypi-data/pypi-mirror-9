# -*- coding: utf-8 -*-
from powerapp.models import todoist_users, integration_periodic_tasks


def run(sync_interval=5):
    while True:
        cron(sync_interval=sync_interval)


def cron(sync_interval=5):
    todoist_users.cron_sync(sync_interval=sync_interval)
    integration_periodic_tasks.cron_run()
