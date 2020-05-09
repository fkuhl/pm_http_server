from tornado.httpclient import HTTPClient, HTTPRequest, HTTPClientError
import json
import pprint
from datetime import date
from pm_data_types.member import Member, MemberStatus, Sex, MaritalStatus, Transaction, TransactionType, Service, ServiceType
from pm_data_types.household import Household
from pm_data_types.address import Address


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
        print(f"read {len(households)} with scope {scope}:")


def main():
    do_read_all("all")
    do_read_all("active")


if __name__ == '__main__':
    main()
