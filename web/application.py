import logging
import time
import traceback

import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado.web import URLSpec

from web import MJGWebModule


class MJGApplication(tornado.web.Application):
    def __init__(self, modules, port=8369):
        super(MJGApplication, self).__init__()
        self.settings = {
            "cookie_secret": "0fa0dc657a749c5a62ef250a57b53b4(&#)(",
            "gzip": True,
            "debug": True,
            "autoreload": False
        }

        self.handlers = []

        path_handlers = MJGWebModule.get_handlers()

        for pattern, handler in path_handlers.iteritems():
            self.handlers.append(URLSpec(pattern, handler))

        self.port = port

    def start(self):

        application = tornado.web.Application(self.handlers, **self.settings)

        http_server = tornado.httpserver.HTTPServer(application, xheaders=True)
        http_server.listen(self.port)

        while True:
            try:
                tornado.ioloop.IOLoop.instance().start()
            except (KeyboardInterrupt, SystemExit):
                logging.info('[!] Program Stopped Manually!')
                self.stop()
                raise
            except:
                logging.error(traceback.format_exc())
                logging.info('[!] Server is restarting in 3 seconds')
                time.sleep(3)

    @staticmethod
    def stop():
        tornado.ioloop.IOLoop.instance().stop()
