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

mem5 = Member()
mem5.family_name = "Peripatetic"
mem5.given_name = "Pam"
mem5.status = MemberStatus.COMMUNING
mem5.date_of_birth = "1997-01-01"


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
        payload = household.clean_json_string
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
        return h


def do_update(id_to_update, household):
    http_client = HTTPClient()
    try:
        request = HTTPRequest(
            url=f"http://localhost:8000/api/Households?id={id_to_update}",
            method="PUT",
            headers={"Content-Type": "application/json; charset=UTF-8"},
            body=household.clean_json_string
        )
        response = http_client.fetch(request)
    except HTTPClientError as e:
        message = e.response.body.decode('utf-8') if e.response else "<none>"
        print(f"Error on update id: {id}, code: {e.code} msg: {message}")
    else:
        resp = response.body.decode('utf-8')
        print(f"resp from update: \"{resp}\"")


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


def do_read_all_members(scope):
    http_client = HTTPClient()
    try:
        request = HTTPRequest(
            url=f"http://localhost:8000/api/Members?scope={scope}",
            method="GET",
            headers={"Content-Type": "application/json; charset=UTF-8"},
            body=None
        )
        response = http_client.fetch(request)
    except HTTPClientError as e:
        message = e.response.body.decode('utf-8') if e.response else "<none>"
        print(
            f"Error on read_all_members with scope {scope}, code: {e.code} msg: {message}")
    else:
        members_json_objs = json.loads(response.body.decode('utf-8'))
        # pp.pprint(members_json_objs)
        members = [Member.make_from_clean_dict(m) for m in members_json_objs]
        print(f"resp from read_all_members with scope {scope}:")
        for m in members:
            print(f"    {m.full_name}")


def do_move_member(old_household, member_id, new_household, relation):
    http_client = HTTPClient()
    try:
        params = f"op=move_member&old_household={old_household}&member_id={member_id}&new_household={new_household}&relation={relation}"
        request = HTTPRequest(
            url=f"http://localhost:8000/api/Transaction?{params}",
            method="PUT",
            headers={"Content-Type": "application/json; charset=UTF-8"},
            body=""
        )
        response = http_client.fetch(request)
    except HTTPClientError as e:
        message = e.response.body.decode('utf-8') if e.response else "<none>"
        print(f"Error on move_member: code: {e.code} msg: {message}")
    else:
        resp = response.body.decode('utf-8')
        print(f"resp from move_member: \"{resp}\"")


def print_members(household):
    if household is None:
        print("no household]")
        return
    spouse_rep = "none" if (
        household.spouse is None) else household.spouse.full_name
    print(f"head: {household.head.full_name} spouse: {spouse_rep} others:")
    for other in household.others:
        print(f"  {other.full_name}")


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
    hh1.head.nickname = "Horry"
    do_update(hh1_id, hh1)  # update
    do_read(hh1_id)  # hh1 head now has nickname
    hh2_id = do_create(hh2)  # restore hh2 to db
    do_read_all_members("all")  # 2 Hornswoggles, 2 Fritzes
    do_read_all_members("active")  # 2 Hornswoggles

    hh1.others.append(mem5)  # add Pam to hh1
    do_update(hh1_id, hh1)  # update
    do_read(hh1_id)  # Pam now in Hornswoggles
    # fail: Franz has a spouse
    do_move_member(hh1_id, mem5.id, hh2_id, "SPOUSE")
    print_members(do_read(hh1_id))  # show transaction failed, no change
    print_members(do_read(hh2_id))
    do_move_member(hh1_id, mem5.id, hh2_id, "OTHER")  # move Pam to Frantzes
    print_members(do_read(hh1_id))  # Pam not in Hornswoggles
    print_members(do_read(hh2_id))  # Pam in Frantzes


if __name__ == '__main__':
    main()
