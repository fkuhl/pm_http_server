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
hh1 = Household()
hh1.head = mem1
hh1.spouse = mem2
hh1.address = addr

mem3 = Member()
mem3.family_name = "Fritz"
mem3.given_name = "Franz"
mem3.status = MemberStatus.DISMISSED
mem3.date_of_birth = "1776-07-04"
mem4 = Member()
mem4.family_name = "Fritz"
mem4.given_name = "Frances"
mem4.status = MemberStatus.DISMISSED
mem4.date_of_birth = "1789-01-01"
hh2 = Household()
hh2.head = mem3
hh2.spouse = mem4
hh2.address = addr


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


def do_drop():
    http_client = HTTPClient()
    try:
        request = HTTPRequest(
            url="http://localhost:8000/api/Households",
            method="DELETE"
        )
        response = http_client.fetch(request)
    except HTTPClientError as e:
        message = e.response.body.decode('utf-8') if e.response else "<none>"
        print(f"Error on drop, code: {e.code} msg: {message}")
    else:
        print(f"resp from drop: \"{response.body.decode('utf-8')}\"")


def do_create_bad_json():
    http_client = HTTPClient()
    try:
        request = HTTPRequest(
            url="http://localhost:8000/api/Households",
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


def do_create(household):
    http_client = HTTPClient()
    try:
        payload = household.clean_json
        # pp.pprint(payload)
        request = HTTPRequest(
            url="http://localhost:8000/api/Households",
            method="POST",
            headers={"Content-Type": "application/json; charset=UTF-8"},
            body=payload
        )
        response = http_client.fetch(request)
    except HTTPClientError as e:
        message = e.response.body.decode('utf-8') if e.response else "<none>"
        print(f"Error on create, code: {e.code} msg: {message}")
    else:
        id_as_str = response.body.decode('utf-8')
        print(f"resp from create: \"{id_as_str}\"")
        return id_as_str


def do_read_all(scope):
    http_client = HTTPClient()
    try:
        request = HTTPRequest(
            url=f"http://localhost:8000/api/Households?scope={scope}",
            method="GET",
            headers={"Content-Type": "application/json; charset=UTF-8"},
            body=None
        )
        response = http_client.fetch(request)
    except HTTPClientError as e:
        message = e.response.body.decode('utf-8') if e.response else "<none>"
        print(
            f"Error on read_all with scope {scope}, code: {e.code} msg: {message}")
    else:
        households_json_objs = json.loads(response.body.decode('utf-8'))
        # pp.pprint(households_json_objs)
        households = [Household.make_from_clean_dict(h)
                      for h in households_json_objs]
        print(f"resp from read_all with scope {scope}:")
        for h in households:
            print(f"    head: {h.head.full_name}")


def do_read(id_to_read):
    http_client = HTTPClient()
    try:
        request = HTTPRequest(
            url=f"http://localhost:8000/api/Households?id={id_to_read}",
            method="GET",
            headers={"Content-Type": "application/json; charset=UTF-8"}
        )
        response = http_client.fetch(request)
    except HTTPClientError as e:
        message = e.response.body.decode('utf-8') if e.response else "<none>"
        print(f"Error on read id: {id}, code: {e.code} msg: {message}")
    else:
        resp = response.body.decode('utf-8')
        h = Household.make_from_clean_dict(json.loads(resp))
        print(f"resp from read: \"{h.head.full_name}\"")


def do_delete(id_to_delete):
    http_client = HTTPClient()
    try:
        request = HTTPRequest(
            url=f"http://localhost:8000/api/Households?id={id_to_delete}",
            method="DELETE",
            headers={"Content-Type": "application/json; charset=UTF-8"}
        )
        response = http_client.fetch(request)
    except HTTPClientError as e:
        message = e.response.body.decode('utf-8') if e.response else "<none>"
        print(f"Error on delete id: {id}, code: {e.code} msg: {message}")
    else:
        resp = response.body.decode('utf-8')
        print(f"resp from delete: \"{resp}\"")


def main():
    do_bad_url()  # 405 error
    do_drop()  # succeeds silently
    do_create_bad_json()  # 400 with decode error
    hh1_id = do_create(hh1)  # returns id
    hh2_id = do_create(hh2)  # returns id
    do_read(hh1_id)         # returns Hornswoggle
    do_read_all("invalid")  # 400 invalid scope
    do_read_all("all")  # Hornswoggle and Frantz households
    do_read_all("active")  # Hornswoggle only
    do_delete(hh2_id)  # succeeds silently
    do_read_all("all")  # Hornswoggle only
    do_delete(hh2_id)  # 404 not found


if __name__ == '__main__':
    main()
