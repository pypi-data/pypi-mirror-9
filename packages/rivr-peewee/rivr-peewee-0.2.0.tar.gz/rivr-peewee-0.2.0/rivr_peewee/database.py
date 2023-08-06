#!/usr/bin/env python

import os

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

import peewee
from playhouse.db_url import connect
from rivr.middleware import Middleware


class Database(Middleware):
    def __init__(self, database=None, env='DATABASE_URL', default=None):
        if database is None:
            url = os.environ.get(env, default)
            if url:
                database = connect(url)

        if database is None:
            raise Exception('Database is not configured.')

        self.database = database
        self.Model = self.get_model_class()

    def process_request(self, request):
        self.database.connect()

    def process_response(self, request, response):
        if not self.database.is_closed():
            self.database.close()

        return response

    def get_model_class(self):
        class Model(peewee.Model):
            class Meta:
                database = self.database

        return Model

    def wrap(self, view):
        def func(request):
            return self.dispatch(view, request)

        return func

    def __call__(self, view):
        return self.wrap(view)

    # With

    def __enter__(self):
        self.database.connect()

    def __exit__(self, *args, **kwargs):
        if not self.database.is_closed():
            self.database.close()

    # Proxy to database

    def create_tables(self, *args, **kwargs):
        return self.database.create_tables(*args, **kwargs)

    def transaction(self, *args, **kwargs):
        return self.database.transaction(*args, **kwargs)

    def atomic(self, *args, **kwargs):
        return self.database.atomic(*args, **kwargs)
