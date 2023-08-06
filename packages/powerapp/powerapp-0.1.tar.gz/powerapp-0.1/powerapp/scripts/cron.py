#!/usr/bin/env python
from powerapp.init import init; init()


from powerapp.eventloop import cron
if __name__ == '__main__':
    cron()
