import rethinkdb
import tornado.gen

from .util import BaseHandler

class DHCPAckApiV1Handler(BaseHandler):
    """
    DHCP Ack API Handler - Log DHCP ack's from dhcp servers.
    """

    def get(self):
        pass

    @tornado.gen.coroutine
    def post(self):
        conn = yield self.application.conn
        yield rethinkdb.table("dhcpack").insert(rethinkdb.json(self.request.body)).run(
            conn)


class DHCPServerStatsApiV1Handler(BaseHandler):
    """
    DHCP Server Stats API Handler - Log aggregated server stats.
    """

    def get(self):
        pass

    @tornado.gen.coroutine
    def post(self):
        conn = yield self.application.conn
        yield rethinkdb.table("dhcpserverstats").insert(rethinkdb.json(self.request.body)).run(
            conn)