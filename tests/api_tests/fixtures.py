import pytest
import tornado.httpserver
import tornado.netutil

import socket
import threading
import random
import logging

from notouch.app import Application
from notouch.util import create_database
from notouch.util import clean_database

class Server(object):
    """ Wrapper around Tornado server with test helpers. """

    def __init__(self):
        tornado_settings = {
            "debug": False
        }
        self.app = Application(tornado_settings)

        # Create a temproary database.
        self.app.rethinkdb_db = "notouch_testing"
        self.rethinkdb_conn = create_database(self.app.rethinkdb_host, self.app.rethinkdb_port,
            self.app.rethinkdb_db)

        self.server = tornado.httpserver.HTTPServer(self.app)
        self.server.add_sockets(tornado.netutil.bind_sockets(
            None, "localhost", family=socket.AF_INET
        ))
        self.server.start()
        self.io_thread = threading.Thread(
            target=tornado.ioloop.IOLoop.instance().start
        )

        logging.getLogger("tornado.access").disabled = True

        self.io_thread.start()

    @property
    def port(self):
        return self.server._sockets.values()[0].getsockname()[1]


@pytest.fixture()
def tornado_server(request):

    server = Server()

    def fin():
        tornado.ioloop.IOLoop.instance().stop()
        server.io_thread.join()

        clean_database(server.rethinkdb_conn, server.app.rethinkdb_db, testing=True)

    request.addfinalizer(fin)

    return server