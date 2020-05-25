import tornado.web
from members_handler import BaseHandler
import logging
from pymongo.read_concern import ReadConcern
from bson import json_util
from bson.objectid import ObjectId
import uuid
import pprint
from pm_data_types.data_common import db_name, collection_name
from pm_data_types.member import Member, MemberStatus, Sex, MaritalStatus, Transaction, TransactionType, Service, ServiceType
from pm_data_types.address import Address
from pm_data_types.household import Household

pp = pprint.PrettyPrinter(indent=4)

# This was proginally written to use a MongoDB transaction.
# Those, however, apply only to Mongo replica sets.
# So instead we perform all the ops in a single handler.
# Who knows, it might be atomic.


class TransactionHandler(BaseHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.req_tag = str(uuid.uuid4())[-4:]
        self.logger = logging.getLogger('HandlerLogger')

    def put(self):
        try:
            op = self.get_query_argument("op")
            self.logger.debug(f"{self.req_tag}: starting put op: {op}")
            if (op == "move_member"):
                old_household = self.get_query_argument("old_household")
                member_id = self.get_query_argument("member_id")
                new_household = self.get_query_argument("new_household")
                relation = self.get_query_argument("relation")
                self.handle_move_member(
                    old_household, member_id, new_household, relation)
                self.set_status(200)
                self.write("")
        except tornado.web.MissingArgumentError:
            self.logger.error(
                f"{self.req_tag}: missing argument", exc_info=True)
            self.set_status(400)
            self.write("missing argument")
            return
        except Exception as e:
            self.logger.error(f"{self.req_tag}: exc: {e}", exc_info=True)
            self.set_status(500)
            self.write(f"exc: {e}")

    def handle_move_member(self, old_household, member_id, new_household, relation):
        collection = self.application.mongo[db_name][collection_name]
        self.logger.debug(
            f"{self.req_tag}: started callback")
        old_h_dict = collection.find_one(
            {'_id': ObjectId(old_household)})
        if old_h_dict is None:
            self.logger.debug(f"{self.req_tag}: didn't old h")
            raise Exception("previous household not found")
        old_h = Household.make_from_mongo_dict(old_h_dict)
        member = None
        old_relation = None
        if (old_h.spouse.id == member_id):
            self.logger.debug(f"{self.req_tag}: member is spouse")
            member = old_h.spouse
            old_relation = "SPOUSE"
        else:
            member_list = [other for other in old_h.others if other.id ==
                           member_id]
            if len(member_list) == 0:
                self.logger.debug(
                    f"{self.req_tag}: member not in old household")
                raise Exception("member not in old household")
            member = member_list[0]
            self.logger.debug(f"{self.req_tag}: member is other")
            old_relation = "OTHER"
        new_h_dict = collection.find_one({'_id': ObjectId(new_household)})
        if new_h_dict is None:
            raise Exception("new household not found")
        self.logger.debug(f"{self.req_tag}: found new h")
        new_h = Household.make_from_mongo_dict(new_h_dict)
        if relation == "SPOUSE" and new_h.spouse is not None:
            raise Exception("attempt to replace spouse")

        # We've checked everything we can, so "commit"
        if old_relation == "SPOUSE":
            old_h.spouse = None
        else:
            old_h.others = [
                other for other in old_h.others if other.id != member.id]
        self.update_household(collection, old_h)

        member.household = new_household  # change Member's household

        if relation == "SPOUSE":
            new_h.spouse = member
        else:
            new_h.others.append(member)
        self.update_household(collection, new_h)
        self.set_status(404)
        self.write("")

    def update_household(self, collection, household):
        mongo_dict = household.mongoize()
        update_filter = {'_id': ObjectId(household.id)}
        result = collection.replace_one(
            update_filter, mongo_dict, upsert=False)
        if result.matched_count != 1:
            raise Exception(
                f"failed up update household {household.head.full_name}")
        self.logger.debug(
            f"{self.req_tag}: updated household {household.head.full_name}")
