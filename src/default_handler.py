import tornado.web
from members_handler import BaseHandler
import logging


class DefaultHandler(BaseHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger('HandlerLogger')

    def prepare(self):
        self.logger.warning("url not found")
        self.set_status(404)
        self.write("url not found")
        return
