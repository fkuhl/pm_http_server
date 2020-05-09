from households_handler import HouseholdsHandler
from members_handler import MembersHandler
from default_handler import DefaultHandler
from file_handler import FileHandler
import os
import sys
import json
from argparse import ArgumentParser
import signal
import tornado.web
import logging
import pymongo
from pymongo import MongoClient

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s : %(levelname)-8s : %(message)s',
    handlers=[
        logging.FileHandler("server.log"),
        logging.StreamHandler(sys.stdout)
    ])
logging.getLogger('asyncio').setLevel(logging.WARNING)
log = logging.getLogger('HandlerLogger')


class PMServer(tornado.web.Application):
    is_closing = False

    def __init__(self, handlers, **settings):
        log.info(settings)
        self.mongo = MongoClient(host=settings['host'], port=settings['port'])
        super(PMServer, self).__init__(handlers, **settings)

    def signal_handler(self, signum, frame):
        log.info('Exiting...')
        self.is_closing = True

    def try_exit(self):
        if self.is_closing:
            tornado.ioloop.IOLoop.instance().stop()
            log.info('Server exited')


def mk_app(prefix, db_host):
    if prefix:
        path = '/' + prefix + '/(.)'
    else:
        path = '/(.)'
    handlers = [
        (path, FileHandler, {"path": os.getcwd()}),
        (r"/api/Members", MembersHandler),
        (r"/api/Households", HouseholdsHandler)
    ]
    settings = dict(
        debug=True,
        host= db_host,
        port=27017,
        default_handler_class=DefaultHandler)
    application = PMServer(handlers, **settings)
    return application


def start_server(prefix, port, db_host):
    app = mk_app(prefix, db_host)
    signal.signal(signal.SIGINT, app.signal_handler)
    app.listen(port)
    log.info('Server listening on port %d' % port)
    tornado.ioloop.PeriodicCallback(app.try_exit, 100).start()
    tornado.ioloop.IOLoop.instance().start()


def parse_args(args=None):
    parser = ArgumentParser(description="...")
    parser.add_argument('-p', '--port', type=int, default=8000,
                        help='The port on which the server will listen')
    # The following two args are for serving a client application or other file
    parser.add_argument('-f', '--prefix', type=str, default="",
                        help="A prefix to add to the location from which pages are served")
    parser.add_argument('-d', '--dir', default='.',
                        help="Directory from which to serve files")
    parser.add_argument('-db', '--db_host', default='localhost',
                        help="Hostname of database server")
    return parser.parse_args()


def main(args=None):
    args = parse_args(args)
    os.chdir(args.dir)
    start_server(prefix=args.prefix, port=args.port, db_host=args.db_host)


if __name__ == '__main__':
    main(sys.argv)
