from tornado.httpclient import HTTPClient
import json
import pprint
from datetime import date
from pm_data_types.member import Member, MemberStatus, Sex, MaritalStatus, Transaction, TransactionType, Service, ServiceType
from pm_data_types.address import Address


def do_drop():
    http_client = HTTPClient()
    try:
        response = http_client.fetch(
            "http://localhost:8000/api/Households?op=drop")
    except Exception as e:
        print("Error: %s" % e)
    else:
        print(f"resp: {response.body}")


def main():
    do_drop()


if __name__ == '__main__':
    main()
