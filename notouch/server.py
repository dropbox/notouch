"""
Physical machine installer automation.
"""
import tornado.web
import tornado.ioloop
import tornado.httpserver

import argparse
import json

from .app import Application


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

    tornado_kwargs = {
        "debug": args.debug,
    }

    app = Application(tornado_kwargs,
        rethinkdb_host=args.rethinkdb_host,
        rethinkdb_port=args.rethinkdb_port,
        rethinkdb_db=args.rethinkdb_db
    )

    print "Starting notouch server on {}:{}...".format(args.address, args.port)

    server = tornado.httpserver.HTTPServer(app)
    server.bind(args.port, args.address)
    if args.debug:
        print "Tornado running in debug mode, spawning single process."
        args.workers = 1
    try:
        server.start(args.workers)
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        tornado.ioloop.IOLoop.instance().stop()
    finally:
        print "Quitting..."
