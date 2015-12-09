import tornado
from .routes import HANDLERS

class Application(tornado.web.Application):

    def __init__(self, tornado_kwargs={}, rethinkdb_host="localhost", rethinkdb_port=28015,
        rethinkdb_db="notouch"):

        tornado_kwargs["handlers"] = HANDLERS

        self.rethinkdb_host = rethinkdb_host
        self.rethinkdb_port = rethinkdb_port
        self.rethinkdb_db = rethinkdb_db
        self.conn = None

        tornado_args = []
        super(Application, self).__init__(*tornado_args, **tornado_kwargs)