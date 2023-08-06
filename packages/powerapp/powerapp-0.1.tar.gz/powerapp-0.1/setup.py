#!/usr/bin/env python
from setuptools import setup, find_packages


def read(filename):
    try:
        return open(filename).read()
    except IOError:
        pass


setup(name='powerapp',
      version='0.1',
      url='https://github.com/Doist/powerapp',
      license='BSD',
      zip_safe=False,
      description='The app to integrate Todoist with third-party services',
      long_description=read('README.rst'),
      packages=find_packages(),
      install_requires=['todoist-python>=0.2.7', 'colorlog', 'peewee',
                        'bottle', 'wtforms>=2', 'requests>=1', 'Mako>=1',
                        'six>=1.9', 'ipython', 'feedparser'],
      entry_points={
          'console_scripts': [
              'powerapp-shell=powerapp.scripts.shell:shell',
              'powerapp-eventloop=powerapp.scripts.eventloop:run',
              'powerapp-cron=powerapp.scripts.cron:cron',
              'powerapp-web=powerapp.scripts.webserver:run',
          ],
      },
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
      ])
