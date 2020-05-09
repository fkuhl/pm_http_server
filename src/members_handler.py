import tornado.web
import logging
import json
import uuid
import pprint
from bson import json_util
import pprint
from pm_data_types.data_common import db_name, collection_name
from pm_data_types.member import Member, MemberStatus, Sex, MaritalStatus, Transaction, TransactionType, Service, ServiceType
from pm_data_types.household import Household


class BaseHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Methods', 'GET PUT POST DELETE')
        self.set_header('Access-Control-Allow-Origin', 'http://localhost:3000')

    def options(self):
        self.set_status(204)
        self.finish()


class MembersHandler(BaseHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.req_tag = str(uuid.uuid4())[-4:]
        self.logger = logging.getLogger('HandlerLogger')

    def get(self):
        try:
            self.handle_read_all()
        except Exception as e:
            self.logger.error(f"{self.req_tag}: exc: {e}", exc_info=True)
            self.write_error(500, message=f"exc: {e}")

    def handle_read_all(self):
        """Read all or only active Members, depending on 'scope' parameter."""
        try:
            scope = self.get_query_argument("scope")
        except tornado.web.MissingArgumentError:
            scope = "invalid"
        if not (scope == "all" or scope == "active"):
            err_msg = 'Invalid scope parameter: %s' % scope
            self.logger.error(err_msg)
            self.set_status(400)
            self.write(err_msg)
            return
        self.logger.debug(f"handle_read_all scope: {scope}")
        collection = self.application.mongo[db_name][collection_name]
        members = []
        for h in collection.find():
            household_obj = Household.make_from_mongo_dict(h)
            members.extend(household_obj.members)
        if scope == "active":
            members = [member for member in members if member.is_active]
        members_json_objs = [json.loads(
            member.clean_json_string) for member in members]
        self.set_status(200)
        self.write(json.dumps(members_json_objs))

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
