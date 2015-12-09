import rethinkdb
import tornado.gen

from .util import BaseHandler, returnsJSON

class MainHandler(BaseHandler):

    @returnsJSON
    @tornado.gen.coroutine
    def get(self):
        conn = yield self.application.conn
        yield rethinkdb.db_list().run(conn)