# Package information
# ===================
import asyncio
import concurrent
import datetime
from functools import partial
import threading

import peewee
from playhouse.shortcuts import model_to_dict, dict_to_model
from playhouse.db_url import connect


class AsyncDatabaseMixin:

    max_connections = 4

    def __init__(self, database, loop=None, **kwargs):
        self.connections = {}
        super().__init__(database, **kwargs)
        self.loop = loop or asyncio.get_event_loop()
        self.threadpool = concurrent.futures.ThreadPoolExecutor(max_workers=self.max_connections)

    @property
    def _Database__local(self):
        tid = threading.get_ident()
        return self.connections.get(tid, peewee._ConnectionLocal())

    @_Database__local.setter
    def _Database__local(self, value):
        tid = threading.get_ident()
        self.connections[tid] = value


class PeeweePlugin(object):

    """ Integrate peewee to bottle. """

    name = 'peewee'
    default_connection = 'sqlite:///db.sqlite'
    max_connections = 2

    def __init__(self, connection=None):
        self.app = None
        self.database = peewee.Proxy()
        self.connection = connection or self.default_connection
        self.serializer = Serializer()
        self.threadpool = concurrent.futures.ThreadPoolExecutor(max_workers=self.max_connections)

    def setup(self, app):
        """ Initialize the application. """

        self.app = app
        app.config.setdefault('PEEWEE_CONNECTION', self.connection)

        self.connection = app.config.get('PEEWEE_CONNECTION')
        self.database.initialize(connect(self.connection))

    def query(self, query):
        if isinstance(query, peewee.SelectQuery):
            return self.run(lambda: list(query))
        return self.run(query.execute)

    @asyncio.coroutine
    def run(self, function, *args, **kwargs):
        """ Run sync code asyncronously. """

        if kwargs:
            function = partial(function, **kwargs)

        def iteration(database, *args):
            database.connect()
            try:
                with database.transaction():
                    return function(*args)
            except peewee.PeeweeException:
                database.rollback()
                raise
            finally:
                database.commit()
                if not database.is_closed():
                    database.close()

        result = yield from self.app.loop.run_in_executor(
            self.threadpool, iteration, self.database,  *args)
        return result

    def to_dict(self, obj, **kwargs):
        return self.serializer.serialize_object(obj, **kwargs)


class Serializer(object):
    date_format = '%Y-%m-%d'
    time_format = '%H:%M:%S'
    datetime_format = ' '.join([date_format, time_format])

    def convert_value(self, value):
        if isinstance(value, datetime.datetime):
            return value.strftime(self.datetime_format)

        if isinstance(value, datetime.date):
            return value.strftime(self.date_format)

        if isinstance(value, datetime.time):
            return value.strftime(self.time_format)

        if isinstance(value, peewee.Model):
            return value.get_id()

        return value

    def clean_data(self, data):
        for key, value in data.items():
            if isinstance(value, dict):
                self.clean_data(value)
            elif isinstance(value, (list, tuple)):
                data[key] = map(self.clean_data, value)
            else:
                data[key] = self.convert_value(value)
        return data

    def serialize_object(self, obj, **kwargs):
        data = model_to_dict(obj, **kwargs)
        return self.clean_data(data)


class Deserializer(object):

    @staticmethod
    def deserialize_object(model, data):
        return dict_to_model(model, data)
