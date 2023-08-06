# -*- coding: utf-8 -*-
"""
Model to store access tokens
"""
import logging
import peewee
from powerapp.database import AbstractModel, db
from powerapp.models.todoist_users import TodoistUser


logger = logging.getLogger(__name__)


EMPTY_SCOPE = '__all__'


class AbstractOAuthToken(AbstractModel):
    client = peewee.CharField(max_length=128, verbose_name='OAuth client name')
    scope = peewee.CharField(max_length=1024, verbose_name='OAuth scope')
    token = peewee.CharField(max_length=1024, verbose_name='OAuth token value')

    class Meta:
        indexes = (
            (('user', 'client', 'scope'), True),
        )

    @classmethod
    def register(cls, user, client, scope, token):
        """
        Register new access token. We accept the `scope` as comma-separated
        list of values, split it, and store every scope item as a separate
        database record.

        In addition, we don't keep duplicates, and we keep unique values for
        (user, client, scope) tuples.

        If scope is empty (some OAuth servers don't use the concept of scope)
        we internally keep the scope under the "__all__" name.
        """
        ret = []
        scope = scope.strip() or EMPTY_SCOPE
        with db.transaction():
            for sc in scope.split(','):
                try:
                    obj = cls.create(user=user, client=client, scope=sc, token=token)
                except peewee.IntegrityError:
                    where_attrs = (
                        cls.user == user,
                        cls.client == client,
                        cls.scope == sc,
                    )
                    cls.update(token=token).where(*where_attrs).execute()
                    obj = cls.get(*where_attrs)
                ret.append(obj)
        return ret


class AccessToken(AbstractOAuthToken):
    user = peewee.ForeignKeyField(TodoistUser, related_name='access_tokens')

    @classmethod
    def get_by_client(cls, user, client):
        return cls.select().where((cls.user == user) and
                                  (cls.client == client))\
                           .first()


class RefreshToken(AbstractOAuthToken):
    user = peewee.ForeignKeyField(TodoistUser, related_name='refresh_token')
