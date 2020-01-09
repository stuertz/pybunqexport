# -*- coding: utf-8 -*-
# flake8: noqa: E501
# pylint: disable=line-too-long,missing-function-docstring

"""
Tests for export.py
"""
import io
import json
import unittest
from .. import export

_DATA = r"""
[
    {
        "alias": {
            "name": "Felix Mustermann",
            "type": "IBAN",
            "value": "NL94BUNQXXXXXXXXX"
        },
        "allow_chat": false,
        "amount": {
            "currency": "EUR",
            "value": "200.00"
        },
        "attachment": [],
        "balance_after_mutation": {
            "currency": "EUR",
            "value": "200.00"
        },
        "counterparty_alias": {
            "name": "bunq",
            "type": "IBAN",
            "value": "NL61BUNQYYYYYYYYYY"
        },
        "created": "2019-12-23 09:56:48.004134",
        "description": "bunq account top up",
        "id": 232997638,
        "monetary_account_id": 1111111,
        "request_reference_split_the_bill": [],
        "sub_type": "PAYMENT",
        "type": "CHECKOUT_MERCHANT",
        "updated": "2019-12-23 09:56:48.004134"
    },
    {
        "alias": {
            "name": "Felix Mustermann",
            "type": "IBAN",
            "value": "NL94BUNQXXXXXXXXX"
        },
        "allow_chat": false,
        "amount": {
            "currency": "EUR",
            "value": "-16.96"
        },
        "attachment": [],
        "balance_after_mutation": {
            "currency": "EUR",
            "value": "183.04"
        },
        "counterparty_alias": {
            "name": "Thank You",
            "type": "IBAN"
        },
        "created": "2019-12-23 17:31:34.703966",
        "description": "Some Company\n",
        "id": 233385317,
        "monetary_account_id": 1111111,
        "request_reference_split_the_bill": [],
        "sub_type": "PAYMENT",
        "type": "MASTERCARD",
        "updated": "2019-12-24 09:36:26.128422"
    },
    {
        "alias": {
            "name": "Felix Mustermann",
            "type": "IBAN",
            "value": "NL94BUNQXXXXXXXXX"
        },
        "allow_chat": false,
        "amount": {
            "currency": "EUR",
            "value": "-0.04"
        },
        "attachment": [],
        "balance_after_mutation": {
            "currency": "EUR",
            "value": "183.00"
        },
        "counterparty_alias": {
            "name": "Felix Mustermann",
            "type": "IBAN",
            "value": "NL45BUNQZZZZZZZZZZ"
        },
        "created": "2019-12-23 17:31:34.856484",
        "description": "",
        "id": 233385323,
        "monetary_account_id": 1111111,
        "request_reference_split_the_bill": [],
        "sub_type": "PAYMENT",
        "type": "SAVINGS",
        "updated": "2019-12-23 17:31:34.856484"
    },
    {
        "alias": {
            "name": "Felix Mustermann",
            "type": "IBAN",
            "value": "NL94BUNQXXXXXXXXX"
        },
        "allow_chat": false,
        "amount": {
            "currency": "EUR",
            "value": "500.00"
        },
        "attachment": [],
        "balance_after_mutation": {
            "currency": "EUR",
            "value": "683.00"
        },
        "counterparty_alias": {
            "name": "Felix Mustermann",
            "type": "IBAN",
            "value": "DE831111111222222222222"
        },
        "created": "2019-12-24 07:00:46.074516",
        "description": "---",
        "id": 233569632,
        "monetary_account_id": 1111111,
        "request_reference_split_the_bill": [],
        "sub_type": "SCT",
        "type": "EBA_SCT",
        "updated": "2019-12-24 07:00:46.074516"
    }
]
"""


class TestPayments(unittest.TestCase):
    """Minimal Testing for Payments Class"""

    def setUp(self):
        self.payments = export.Payments(_DATA)

    def test_csv_lexware(self):
        fobj = io.StringIO()
        self.payments.to_csv(fobj, 'lexware')
        self.assertEqual(fobj.getvalue(),
                         'allow_chat,attachment,created,description,id,monetary_account_id,request_reference_split_the_bill,sub_type,type,updated,alias.name,alias.type,alias.value,amount.currency,amount.value,balance_after_mutation.currency,balance_after_mutation.value,counterparty_alias.name,counterparty_alias.type,counterparty_alias.value\r\n'
                         'False,[],23.12.2019,bunq account top up,232997638,1111111,[],PAYMENT,CHECKOUT_MERCHANT,23.12.2019,Felix Mustermann,IBAN,NL94BUNQXXXXXXXXX,EUR,200.00,EUR,200.00,bunq,IBAN,NL61BUNQYYYYYYYYYY\r\n'
                         'False,[],23.12.2019,"Some Company\n",233385317,1111111,[],PAYMENT,MASTERCARD,24.12.2019,Felix Mustermann,IBAN,NL94BUNQXXXXXXXXX,EUR,-16.96,EUR,183.04,Thank You,IBAN,\r\n'
                         'False,[],23.12.2019,,233385323,1111111,[],PAYMENT,SAVINGS,23.12.2019,Felix Mustermann,IBAN,NL94BUNQXXXXXXXXX,EUR,-0.04,EUR,183.00,Felix Mustermann,IBAN,NL45BUNQZZZZZZZZZZ\r\n'
                         'False,[],24.12.2019,---,233569632,1111111,[],SCT,EBA_SCT,24.12.2019,Felix Mustermann,IBAN,NL94BUNQXXXXXXXXX,EUR,500.00,EUR,683.00,Felix Mustermann,IBAN,DE831111111222222222222\r\n')

    def test_csv(self):
        fobj = io.StringIO()
        self.payments.to_csv(fobj)
        self.assertEqual(fobj.getvalue(),
                         'allow_chat,attachment,created,description,id,monetary_account_id,request_reference_split_the_bill,sub_type,type,updated,alias.name,alias.type,alias.value,amount.currency,amount.value,balance_after_mutation.currency,balance_after_mutation.value,counterparty_alias.name,counterparty_alias.type,counterparty_alias.value\r\n'
                         'False,[],2019-12-23 09:56:48.004134,bunq account top up,232997638,1111111,[],PAYMENT,CHECKOUT_MERCHANT,2019-12-23 09:56:48.004134,Felix Mustermann,IBAN,NL94BUNQXXXXXXXXX,EUR,200.00,EUR,200.00,bunq,IBAN,NL61BUNQYYYYYYYYYY\r\n'
                         'False,[],2019-12-23 17:31:34.703966,"Some Company\n",233385317,1111111,[],PAYMENT,MASTERCARD,2019-12-24 09:36:26.128422,Felix Mustermann,IBAN,NL94BUNQXXXXXXXXX,EUR,-16.96,EUR,183.04,Thank You,IBAN,\r\n'
                         'False,[],2019-12-23 17:31:34.856484,,233385323,1111111,[],PAYMENT,SAVINGS,2019-12-23 17:31:34.856484,Felix Mustermann,IBAN,NL94BUNQXXXXXXXXX,EUR,-0.04,EUR,183.00,Felix Mustermann,IBAN,NL45BUNQZZZZZZZZZZ\r\n'
                         'False,[],2019-12-24 07:00:46.074516,---,233569632,1111111,[],SCT,EBA_SCT,2019-12-24 07:00:46.074516,Felix Mustermann,IBAN,NL94BUNQXXXXXXXXX,EUR,500.00,EUR,683.00,Felix Mustermann,IBAN,DE831111111222222222222\r\n')

    def test_json(self):
        fobj = io.StringIO()
        self.payments.to_json(fobj)
        print(fobj.getvalue())
        self.assertEqual(json.loads(fobj.getvalue()),
                         json.loads(r'''[
  {
    "allow_chat": false,
    "attachment": [],
    "created": "2019-12-23T09:56:48.004Z",
    "description": "bunq account top up",
    "id": 232997638,
    "monetary_account_id": 1111111,
    "request_reference_split_the_bill": [],
    "sub_type": "PAYMENT",
    "type": "CHECKOUT_MERCHANT",
    "updated": "2019-12-23T09:56:48.004Z",
    "alias.name": "Felix Mustermann",
    "alias.type": "IBAN",
    "alias.value": "NL94BUNQXXXXXXXXX",
    "amount.currency": "EUR",
    "amount.value": "200.00",
    "balance_after_mutation.currency": "EUR",
    "balance_after_mutation.value": "200.00",
    "counterparty_alias.name": "bunq",
    "counterparty_alias.type": "IBAN",
    "counterparty_alias.value": "NL61BUNQYYYYYYYYYY"
  },
  {
    "allow_chat": false,
    "attachment": [],
    "created": "2019-12-23T17:31:34.703Z",
    "description": "Some Company\n",
    "id": 233385317,
    "monetary_account_id": 1111111,
    "request_reference_split_the_bill": [],
    "sub_type": "PAYMENT",
    "type": "MASTERCARD",
    "updated": "2019-12-24T09:36:26.128Z",
    "alias.name": "Felix Mustermann",
    "alias.type": "IBAN",
    "alias.value": "NL94BUNQXXXXXXXXX",
    "amount.currency": "EUR",
    "amount.value": "-16.96",
    "balance_after_mutation.currency": "EUR",
    "balance_after_mutation.value": "183.04",
    "counterparty_alias.name": "Thank You",
    "counterparty_alias.type": "IBAN",
    "counterparty_alias.value": null
  },
  {
    "allow_chat": false,
    "attachment": [],
    "created": "2019-12-23T17:31:34.856Z",
    "description": "",
    "id": 233385323,
    "monetary_account_id": 1111111,
    "request_reference_split_the_bill": [],
    "sub_type": "PAYMENT",
    "type": "SAVINGS",
    "updated": "2019-12-23T17:31:34.856Z",
    "alias.name": "Felix Mustermann",
    "alias.type": "IBAN",
    "alias.value": "NL94BUNQXXXXXXXXX",
    "amount.currency": "EUR",
    "amount.value": "-0.04",
    "balance_after_mutation.currency": "EUR",
    "balance_after_mutation.value": "183.00",
    "counterparty_alias.name": "Felix Mustermann",
    "counterparty_alias.type": "IBAN",
    "counterparty_alias.value": "NL45BUNQZZZZZZZZZZ"
  },
  {
    "allow_chat": false,
    "attachment": [],
    "created": "2019-12-24T07:00:46.074Z",
    "description": "---",
    "id": 233569632,
    "monetary_account_id": 1111111,
    "request_reference_split_the_bill": [],
    "sub_type": "SCT",
    "type": "EBA_SCT",
    "updated": "2019-12-24T07:00:46.074Z",
    "alias.name": "Felix Mustermann",
    "alias.type": "IBAN",
    "alias.value": "NL94BUNQXXXXXXXXX",
    "amount.currency": "EUR",
    "amount.value": "500.00",
    "balance_after_mutation.currency": "EUR",
    "balance_after_mutation.value": "683.00",
    "counterparty_alias.name": "Felix Mustermann",
    "counterparty_alias.type": "IBAN",
    "counterparty_alias.value": "DE831111111222222222222"
  }
]'''))

    def test_repr(self):
        self.assertEqual([l.rstrip() for l in str(self.payments).split('\n')],
                         ['created    type               counterparty_alias.name amount.currency amount.value description',
                          '23.12.2019  CHECKOUT_MERCHANT              bunq        EUR             200.00       bunq account top up',
                          '23.12.2019         MASTERCARD         Thank You        EUR             -16.96              Some Company',
                          '23.12.2019            SAVINGS  Felix Mustermann        EUR              -0.04',
                          '24.12.2019            EBA_SCT  Felix Mustermann        EUR             500.00                       ---'])

    def test_len(self):
        self.assertEqual(len(self.payments),
                         4)
