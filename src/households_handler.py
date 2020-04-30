import tornado.web
from members_handler import BaseHandler
import logging
from bson import json_util
import json
import uuid


class HouseholdsHandler(BaseHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.req_tag = str(uuid.uuid4())[-4:]
        self.logger = logging.getLogger('HandlerLogger')
        self.logger.info(f"{self.req_tag}: instantiating HouseholdsHandler")

    def get(self):
        try:
            op = self.get_argument("op")
            self.logger.info(f"{self.req_tag}: HH got op {op}")
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
            self.set_status(200)
            self.write("op till you drop")
            self.logger.info(f"{self.req_tag}: done")
            return
        except Exception as e:
            self.logger.error(f"{self.req_tag}: exc: {e}", exc_info=True)
            self.set_status(500)
            self.write(f"exc: {e}")
