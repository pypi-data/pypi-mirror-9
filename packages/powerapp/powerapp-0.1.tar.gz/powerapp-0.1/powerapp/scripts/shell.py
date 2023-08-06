#!/usr/bin/env python
from powerapp.init import init; init()
from IPython import embed
import getpass

import argparse
from importlib import import_module
from powerapp.models.todoist_users import TodoistUser
from powerapp.database import models, create_all, drop_all
from powerapp.config import config


def shell():
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--email', help='user email')
    parser.add_argument('-t', '--token', help='user token')
    parser.add_argument('--reset-db', help='reset database', action='store_true')
    args = parser.parse_args()

    if args.reset_db:
        drop_all()
        create_all()

    user = None
    if args.token:
        user = TodoistUser.register(args.token)

    elif args.email:
        user = TodoistUser.select().where(TodoistUser.email == args.email).first()
        if not user:
            prompt = 'Please provide password for %s: ' % args.email
            password = getpass.getpass(prompt)
            user = TodoistUser.register(email=args.email, password=password)

    banner_chunks = []
    if user:
        banner_chunks.append('Logged in as %s' % user.email)

    ns = {'user': user, 'config': config}

    # import models
    banner_chunks.append('\nFollowing models available as global objects:\n')
    for model in models():
        model_name = model.mro()[0].__name__
        ns[model_name] = model
        banner_chunks.append('    %s' % model_name)

    banner_chunks.append('\nFollowing modules were imported for you:\n')
    imports = [
        'powerapp.services',
        'powerapp.database',
    ]
    for imp in imports:
        local_name = imp.split('.')[1]
        ns[local_name] = import_module(imp)
        banner_chunks.append('    %s as %s' % (imp, local_name))

    embed(user_ns=ns, banner2='\n'.join(banner_chunks) + '\n')


if __name__ == '__main__':
    shell()
