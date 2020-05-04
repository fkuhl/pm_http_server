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

    def get(self):
        try:
            id = self.get_query_argument("id")
            self.handle_read(id)
        except tornado.web.MissingArgumentError:
            self.handle_read_all()
        except Exception as e:
            self.logger.error(f"{self.req_tag}: exc: {e}", exc_info=True)
            self.write_error(500, message=f"exc: {e}")

    def put(self):
        try:
            self.handle_update()
        except Exception as e:
            self.logger.error(f"{self.req_tag}: exc: {e}", exc_info=True)
            self.write_error(500, message=f"exc: {e}")

    def post(self):
        try:
            self.handle_create()
        except Exception as e:
            self.logger.error(f"{self.req_tag}: exc: {e}", exc_info=True)
            self.write_error(500, message=f"exc: {e}")

    def delete(self):
        try:
            id = self.get_query_argument("id")
            self.handle_delete(id)
        except tornado.web.MissingArgumentError:
            self.handle_drop()
        except Exception as e:
            self.logger.error(f"{self.req_tag}: exc: {e}", exc_info=True)
            self.write_error(500, message=f"exc: {e}")

    def handle_create(self):
        """Create new Household from request body. Return new id."""
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

    def handle_read(self, id):
        """Read Household with id given as query parameter."""
        pass

    def handle_read_all(self):
        """Read all or only active Households, depending on 'scope' parameter."""
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

    def handle_update(self):
        """Update Household with new value provided."""
        # Decode new value from request body
        # Return status indicates success
        pass

    def handle_drop(self):
        """Drop entire Households collection. Not recommended"""
        self.logger.info(f"{self.req_tag}: about to drop")
        collection = self.application.mongo[db_name][collection_name]
        collection.drop()
        self.logger.info(f"{self.req_tag}: drop succeeded")
        self.set_status(200)
        self.write("")
        return

    def handle_delete(self, id):
        """Delete Household specified by id."""
        pass
