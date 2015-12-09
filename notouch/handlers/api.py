import rethinkdb as r
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
        yield r.table("dhcpack").insert(r.json(self.request.body)).run(
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
        yield r.table("dhcpserverstats").insert(r.json(self.request.body)).run(
            conn)