"""
Physical machine installer automation.
"""
import argparse
import json

import rethinkdb as r

import tornado.web
import tornado.ioloop
import tornado.httpserver


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
            app.conn = r.connect(host=host, port=port, db=db)

    def on_finish(self):
        pass

class MainHandler(BaseHandler):

    @returnsJSON
    def get(self):
        return r.db_list().run(self.application.conn)


class DHCPAckHandler(BaseHandler):
    """
    DHCP Ack API Handler - Log DHCP ack's from dhcp servers.
    """

    def get(self):
        pass

    def post(self):
        r.table("dhcpack").insert(r.json(self.request.body)).run(self.application.conn)


class DHCPServerStatsHandler(BaseHandler):
    """
    DHCP Server Stats API Handler - Log aggregated server stats.
    """

    def get(self):
        pass

    def post(self):
        r.table("dhcpserverstats").insert(r.json(self.request.body)).run(self.application.conn)

def main():

    parser = argparse.ArgumentParser(description="PHIT Installer Automation API Server")

    parser.add_argument("--port", dest="port", type=int, default=8080,
        help="Port to run the server on.")
    parser.add_argument("--address", dest="address", type=str, default="localhost",
        help="Address to run the server on.")
    parser.add_argument("--workers", dest="workers", type=int, default=4,
        help="Number of tornado workers to spawn.")
    parser.add_argument("--rethinkdb_host", dest="rethinkdb_host", type=str, default="localhost",
        help="Hostname for the rethinkdb server to use.")
    parser.add_argument("--rethinkdb_port", dest="rethinkdb_port", type=int, default=28015,
        help="Port that the rethinkdb server runs on.")
    parser.add_argument("--rethinkdb_db", dest="rethinkdb_db", type=str, default="notouch",
        help="Default database to use for rethinkdb.")
    parser.add_argument("--debug", dest="debug", action="store_true", default=False,
        help="Run the tornado web server in debug mode.")

    args = parser.parse_args()

    app = tornado.web.Application([
        (r"/", MainHandler),
        (r"/api/v1/dhcp/ack", DHCPAckHandler),
        (r"/api/v1/dhcp/server_stats", DHCPServerStatsHandler),
    ], debug=args.debug)
    app.rethinkdb_host = args.rethinkdb_host
    app.rethinkdb_port = args.rethinkdb_port
    app.rethinkdb_db = args.rethinkdb_db
    app.conn = None

    server = tornado.httpserver.HTTPServer(app)
    server.bind(args.port, args.address)
    if args.debug:
        print "Tornado running in debug mode can not use multi-process."
        args.workers = 1
    try:
        server.start(args.workers)
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        tornado.ioloop.IOLoop.instance().stop()
    finally:
        print "Quitting..."
