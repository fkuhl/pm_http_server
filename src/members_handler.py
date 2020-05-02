import tornado.web
import logging
import json
from bson import json_util


class BaseHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Methods', 'GET PUT POST DELETE')

    def options(self):
        self.set_status(204)
        self.finish()


class MembersHandler(BaseHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger('HandlerLogger')
        self.logger.info("instantiating MembersHandler")

    def get(self):
        pass
        # scope = self.get_argument('scope')
        # if scope == 'all':
        #     self.logger.debug('Get All Members')
        # elif scope == 'active':
        #     self.logger.debug('Get Active Members')
        # else:
        #     err_msg = 'Invalid scope parameter: %s' % scope
        #     self.logger.error(err_msg)
        #     self.set_status(400)
        #     self.write(err_msg)
        #     return
        # client = self.application.mongo
        # query = {}
        # if scope == 'active':
        #     query = {"$or": [
        #         {"status": "COMMUNING"},
        #         {"status": "NONCOMMUNING"}
        #     ]}
        # data = client.PeriMeleon['Members'].find(query)
        # data = list(data)
        # self.logger.info('%d records found' % len(data))
        # self.set_status(200)
        # self.write(json.dumps(data, default=json_util.default))
