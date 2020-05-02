import tornado.web
from members_handler import BaseHandler
import logging
from bson import json_util
import json
import uuid
import pprint
from pm_data_types.data_common import db_name, collection_name
from pm_data_types.member import Member, MemberStatus, Sex, MaritalStatus, Transaction, TransactionType, Service, ServiceType
from pm_data_types.address import Address
from pm_data_types.household import Household

pp = pprint.PrettyPrinter(indent=4)


class HouseholdsHandler(BaseHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.req_tag = str(uuid.uuid4())[-4:]
        self.logger = logging.getLogger('HandlerLogger')
        self.get_handler_table = {
            "read": self.handle_read,
            "read_all": self.handle_read_all
        }
        self.post_handler_table = {
            "create": self.handle_create,
        }
        self.delete_handler_table = {
            "drop": self.handle_drop,
        }

    def get(self):
        self.dispatch(self.get_handler_table)

    def post(self):
        self.dispatch(self.post_handler_table)

    def delete(self):
        self.dispatch(self.delete_handler_table)

    def dispatch(self, handler_table):
        try:
            op = self.get_argument("op")
            self.logger.info(f"{self.req_tag}: HH got op {op}")
            handler_table[op]()
            return
        except KeyError:
            error_message = f"unrecognized operation: {op}"
            self.logger.warning(f"{self.req_tag}: {error_message}")
            self.set_status(400)
            self.write(error_message)
            return
        except Exception as e:
            self.logger.error(f"{self.req_tag}: exc: {e}", exc_info=True)
            # self.set_status(500)
            self.write_error(500, message=f"exc: {e}")

    def handle_drop(self):
        self.logger.info(f"{self.req_tag}: about to drop")
        collection = self.application.mongo[db_name][collection_name]
        collection.drop()
        self.logger.info(f"{self.req_tag}: drop succeeded")
        self.set_status(200)
        self.write("")
        return

    def handle_create(self):
        self.logger.info(f"{self.req_tag}: about to create")
        try:
            clean_dict = self.request.body.decode('utf-8')
            household_json = json.loads(clean_dict)
            # pp.pprint(household_json)
            household = Household.make_from_clean_dict(household_json)
            mongo_dict = household.mongoize()
        except json.JSONDecodeError as e:
            # capture error early before context changes
            error_message = f"decode error {e}"
            self.logger.warning(f"{self.req_tag}: {error_message}")
            self.set_status(400)
            self.write(error_message)
            return
        collection = self.application.mongo[db_name][collection_name]
        result = collection.insert_one(mongo_dict)
        id_as_str = str(result.inserted_id)
        self.logger.info(
            f"{self.req_tag}: insert succeeded, result: {id_as_str}")
        self.set_status(200)
        self.write(id_as_str)
        return

    def handle_read(self):
        pass

    def handle_read_all(self):
        pass
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
