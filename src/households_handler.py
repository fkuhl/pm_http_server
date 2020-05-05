import tornado.web
from members_handler import BaseHandler
import logging
from bson import json_util
from bson.objectid import ObjectId
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
            id_to_read = self.get_query_argument("id")
            self.handle_read(id_to_read)
        except tornado.web.MissingArgumentError:
            self.handle_read_all()
        except Exception as e:
            self.logger.error(f"{self.req_tag}: exc: {e}", exc_info=True)
            self.write_error(500, message=f"exc: {e}")

    def put(self):
        try:
            id_to_update = self.get_query_argument("id")
            self.handle_update(id_to_update)
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
            id_to_delete = self.get_query_argument("id")
            self.handle_delete(id_to_delete)
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

    def handle_read(self, id_to_read):
        """Read Household with id given as query parameter."""
        collection = self.application.mongo[db_name][collection_name]
        result = collection.find_one({'_id': ObjectId(id_to_read)})
        if result is not None:
            self.set_status(200)
            household_obj = Household.make_from_mongo_dict(result)
            household_json = household_obj.clean_json
            self.write(household_json)
        else:
            self.set_status(404)
            self.write("")

    def handle_read_all(self):
        """Read all or only active Households, depending on 'scope' parameter."""
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
        query = {
            "_Household__head._Member__is_active": True} if scope == 'active' else {}
        household_json_objs = []
        for h in collection.find(query):
            # pp.pprint(h)
            household_obj = Household.make_from_mongo_dict(h)
            household_json_objs.append(json.loads(household_obj.clean_json))
        self.set_status(200)
        self.write(json.dumps(household_json_objs))

    def handle_update(self, id_to_update):
        """Update Household with new value provided."""
        clean_dict = self.request.body.decode('utf-8')
        household_json = json.loads(clean_dict)
        # pp.pprint(household_json)
        household = Household.make_from_clean_dict(household_json)
        mongo_dict = household.mongoize()
        collection = self.application.mongo[db_name][collection_name]
        filter = {'_id': ObjectId(id_to_update)}
        result = collection.replace_one(filter, mongo_dict, upsert=False)
        if result.matched_count != 1:
            self.set_status(404)
            self.write("")
            return
        if result.modified_count != 1:
            self.set_status(400)  # not sure why would fail to modify
            self.write("")
            return
        self.set_status(200)
        self.write("")

    def handle_drop(self):
        """Drop entire Households collection. Not recommended"""
        self.logger.info(f"{self.req_tag}: about to drop")
        collection = self.application.mongo[db_name][collection_name]
        collection.drop()
        self.logger.info(f"{self.req_tag}: drop succeeded")
        self.set_status(200)
        self.write("")
        return

    def handle_delete(self, id_to_delete):
        """Delete Household specified by id."""
        collection = self.application.mongo[db_name][collection_name]
        result = collection.delete_one({'_id': ObjectId(id_to_delete)})
        if result.deleted_count == 1:
            self.set_status(200)
            self.write("")
        else:
            self.set_status(404)
            self.write("")
