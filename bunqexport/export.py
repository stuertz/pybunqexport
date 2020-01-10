#!/usr/bin/env python -W ignore
# -*- coding: utf-8 -*-
"""
Connect to bunq api and create a csv file with all latest payments.

'mode' lexware is to support importing the csv into Lexware
Finazmanger via 'Datei / Export/Import / Datenimport... / Umsätze', or
even better with the Vorlagen.dat (FM does not support isodates)

"""

import argparse
import io
import json
import logging
import sys

import pandas

from bunq.sdk import client
from bunq.sdk import context
from bunq.sdk.model import generated

__all__ = ['main']

_log = logging.getLogger(__name__)  # pylint: disable=invalid-name


def _setup_context(conf):
    """setup the context (login, etc) to work with bunq api"""
    _log.info('Using conf: %s', conf)
    api_context = context.ApiContext.restore(conf)
    api_context.ensure_session_active()
    api_context.save(conf)
    context.BunqContext.load_api_context(api_context)


def _get_all_payments(count, account_id=None):
    """Fetch all Payments wie bunq api in bunq_sdk format"""
    pagination = client.Pagination()
    pagination.count = count
    result = generated.endpoint.Payment.list(
        monetary_account_id=account_id,
        params=pagination.url_params_count_only).value
    _log.info('found %d while fetching last %d Payments for account %s',
              len(result), count, account_id)
    return result


class Payments():
    """
    Abstraction over bunq payments using a pandas dataframe

    payments are served in json
    """

    def __init__(self, payments):
        self.payments = pandas.io.json.json_normalize(json.loads(payments))
        self.payments['created'] = pandas.to_datetime(self.payments['created'])
        self.payments['updated'] = pandas.to_datetime(self.payments['updated'])

    def __repr__(self):
        return self.payments.to_string(
            columns=('created',
                     'type',
                     'counterparty_alias.name',
                     'amount.currency',
                     'amount.value',
                     'description'),
            show_dimensions=False,
            index=False,
            justify='left',
            formatters={
                'created': lambda x: x.strftime('%d.%m.%Y'),
                'description': lambda x: x.replace('\n', ' ').strip(),
            })

    def to_csv(self, fobj, mode=None):
        """Create a csv export from bunq data"""
        if mode == 'lexware':
            self.payments.to_csv(fobj, date_format='%d.%m.%Y',
                                 index=False, line_terminator='\r\n')
        else:
            self.payments.to_csv(fobj, index=False, line_terminator='\r\n')

    def to_json(self, fobj):
        """Create a json export from flattened (depth=1) bunq data"""
        self.payments.to_json(fobj, orient='records', date_format='iso')

    def __len__(self):
        return len(self.payments)


class Accounts():  # pylint: disable=too-few-public-methods
    """
    represent balances of of all active accounts
    """

    def __init__(self):
        pagination = client.Pagination()
        pagination.count = 50

        all_accounts = generated.endpoint.MonetaryAccountBank.list(
            pagination.url_params_count_only).value

        all_accounts.extend(generated.endpoint.MonetaryAccountSavings.list(
            pagination.url_params_count_only).value)

        all_accounts.extend(generated.endpoint.MonetaryAccountJoint.list(
            pagination.url_params_count_only).value)

        self.balances = {
            aacc.id_: (aacc.description, aacc.balance.currency,
                       aacc.balance.value, aacc.description)
            for aacc in (monetary_account_bank
                         for monetary_account_bank in all_accounts
                         if monetary_account_bank.status == 'ACTIVE')}

    def ids(self):
        """
        return tuple of account id and description
        """
        for id_, val in self.balances.items():
            yield id_, val[3]

    def __repr__(self):
        return '\n'.join((f'{v[0]} ({k}): {v[2]} {v[1]}'
                          for k, v in self.balances.items()))


def _export(fname, payments, user, account_name, mode):
    """Do the exporting in various formats"""
    if fname is None:
        fname = 'bunq_%s' % user.id_
    fname += '_%s' % account_name
    with io.open(fname + '.csv', 'w') as fobj:
        payments.to_csv(fobj, mode)
        _log.info('Wrote %s', fname + '.csv')
    with io.open(fname + '.json', 'w') as fobj:
        payments.to_json(fobj)
        _log.info('Wrote %s', fname + '.json')


def main():
    """main entrypoint"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--conf', default='bunq-sandbox.conf',
                        help='api config file')
    parser.add_argument('--outfile', '-o', default=None,
                        help='name of the export csv file')
    parser.add_argument('--payments', default=200,
                        help='Number of payments')
    parser.add_argument('--verbose', '-v', default=False, action='store_true')
    parser.add_argument('--mode', choices=['raw', 'lexware'], default='raw')

    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format='[%(levelname)-7s] %(message)s',
                        stream=sys.stderr)
    # connect
    _setup_context(args.conf)
    user = generated.endpoint.User.get().value.get_referenced_object()

    accounts = Accounts()

    for account_id, account_name in accounts.ids():
        data = ('[' +
                ','.join(p.to_json()
                         for p in reversed(_get_all_payments(
                             args.payments, account_id))) +
                ']')
        payments = Payments(data)
        _export(args.outfile, payments, user, account_name, args.mode)
        print(payments)

    print(accounts)

    # disconnect
    context.BunqContext.api_context().save(args.conf)


if __name__ == '__main__':
    main()
