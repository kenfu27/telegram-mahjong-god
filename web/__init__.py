import tornado.web


class MJGWebModule(object):
    path_handlers = {}

    @classmethod
    def register_handler(cls, pattern):
        def wrapper_class(handler_class):
            cls.path_handlers.update({pattern: handler_class})
            return handler_class

        return wrapper_class

    @classmethod
    def get_handlers(cls):
        return cls.path_handlers


class MJGRequestHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass
