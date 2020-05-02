from tornado.httpclient import HTTPClient, HTTPRequest, HTTPClientError
import json
import pprint
from datetime import date
from pm_data_types.member import Member, MemberStatus, Sex, MaritalStatus, Transaction, TransactionType, Service, ServiceType
from pm_data_types.household import Household
from pm_data_types.address import Address

pp = pprint.PrettyPrinter(indent=4)

mem1 = Member()
mem1.family_name = "Hornswoggle"
mem1.given_name = "Horatio"
mem1.status = MemberStatus.COMMUNING
mem1.date_of_birth = "1776-07-04"
mem2 = Member()
mem2.family_name = "Hornswoggle"
mem2.given_name = "Hortense"
mem2.status = MemberStatus.COMMUNING
mem2.date_of_birth = "1789-01-01"
addr = Address()
addr.address = "123 Pleasant Lane"
addr.city = "Anytown"
addr.state = "VA"
addr.postal_code = "12345"
household = Household()
household.head = mem1
household.spouse = mem2
household.address = addr


def do_bad_url():
    http_client = HTTPClient()
    try:
        response = http_client.fetch(
            "http://localhost:8000/api/badapi")
    except HTTPClientError as e:
        message = e.response.body.decode('utf-8') if e.response else "<none>"
        print(f"Error on bad url, code: {e.code} msg: {message}")
    else:
        print(f"do_bad_url: resp: {response.body.decode('utf-8')}")


def do_bad_op():
    http_client = HTTPClient()
    try:
        response = http_client.fetch(
            "http://localhost:8000/api/Households?op=loco")
    except HTTPClientError as e:
        message = e.response.body.decode('utf-8') if e.response else "<none>"
        print(f"Error on bad op, code: {e.code} msg: {message}")
    else:
        print(f"do_bad_op: resp: {response.body.decode('utf-8')}")


def do_drop():
    http_client = HTTPClient()
    try:
        request = HTTPRequest(
            url="http://localhost:8000/api/Households?op=drop",
            method="DELETE"
        )
        response = http_client.fetch(request)
    except Exception as e:
        print("Error: %s" % e)
    else:
        print(f"resp from drop: \"{response.body.decode('utf-8')}\"")


def do_create_bad_json():
    http_client = HTTPClient()
    try:
        request = HTTPRequest(
            url="http://localhost:8000/api/Households?op=create",
            method="POST",
            headers={"Content-Type": "application/json; charset=UTF-8"},
            body='{"bad json"}'
        )
        response = http_client.fetch(request)
    except HTTPClientError as e:
        message = e.response.body.decode('utf-8') if e.response else "<none>"
        print(f"Error on create bad json, code: {e.code} msg: {message}")
    else:
        resp = response.body.decode('utf-8')
        print(
            f"resp status: {response.code} reason: {response.reason} err: {response.error} body: \"{resp}\"")
        return resp


def do_create():
    http_client = HTTPClient()
    try:
        payload = household.clean_json
        # pp.pprint(payload)
        request = HTTPRequest(
            url="http://localhost:8000/api/Households?op=create",
            method="POST",
            headers={"Content-Type": "application/json; charset=UTF-8"},
            body=payload
        )
        response = http_client.fetch(request)
    except Exception as e:
        print("Error on create: %s" % e)
    else:
        id_as_str = response.body.decode('utf-8')
        print(f"resp from create: \"{id_as_str}\"")
        return id_as_str


def main():
    do_bad_url()
    do_bad_op()
    do_drop()
    do_create_bad_json()
    household_id = do_create()


if __name__ == '__main__':
    main()
