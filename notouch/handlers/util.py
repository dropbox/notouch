import tornado.web
import rethinkdb

import json


def json_serializer(obj):
    """
    A default json serializer that attempts to convert python date objects
        into a string.
    """
    if hasattr(obj, "isoformat"):
        return obj.isoformat()
    raise TypeError


def returnsJSON(func):
    """
    Python decorator for handlers returning JSON data.

    * Sets Content-Type header to application/json.
    * Takes return value and calls json.dump with a safe converter for objects
        like datetimes that won't serialize into json.
    * Calls "write" to return data to the client.
    """
    def dec(self, *args, **kwargs):
        ret = func(self, *args, **kwargs)
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(ret, default=json_serializer))
        return None
    return dec


class BaseHandler(tornado.web.RequestHandler):
    """
    Base class for all handlers which creates a rethinkdb database connection
    object per application object for multi-processs safety.
    """
    def initialize(self):
        app = self.application
        if app.conn is None:
            host = app.rethinkdb_host
            port = app.rethinkdb_port
            db = app.rethinkdb_db
            rethinkdb.set_loop_type("tornado")
            app.conn = rethinkdb.connect(host=host, port=port, db=db)

    def on_finish(self):
        pass