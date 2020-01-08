#!/usr/bin/env python -W ignore
# -*- coding: utf-8; mode: python -*-
"""
Connect to bunq api and create a csv file with all latest payments.

'mode' lexware is to support importing the csv into Lexware
Finazmanger via 'Datei / Export/Import / Datenimport... / Umsätze', or
even better with the Vorlagen.dat (FM does not support isodates)

"""

import argparse
import json
import logging
import sys

import pandas

from bunq.sdk import client
from bunq.sdk import context
from bunq.sdk.model import generated

__all__ = ['main']

_log = logging.getLogger(__name__)


def _setup_context(conf):
    """setup the context (login, etc) to work with bunq api"""
    _log.info("Using conf: %s", conf)
    api_context = context.ApiContext.restore(conf)
    api_context.ensure_session_active()
    api_context.save(conf)
    context.BunqContext.load_api_context(api_context)


def _get_all_payments(count):
    """Fetch all Payments wie bunq api in bunq_sdk format"""
    pagination = client.Pagination()
    pagination.count = count
    result = generated.endpoint.Payment.list(
        params=pagination.url_params_count_only).value
    _log.info('found %d while fetching last %d Payments', len(result), count)
    return result


class Payments():
    """
    Abstraction over bunq payments using a pandas dataframe
    """
    def __init__(self, payments):
        data = (json.loads(p.to_json()) for p in reversed(payments))
        self.payments = pandas.io.json.json_normalize(data)
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
                'created': lambda x: x.strftime("%d.%m.%Y"),
                'description': lambda x: x.replace("\n", " ").strip(),
            })

    def to_csv(self, fname, mode):
        """Create a csv export from bunq data"""
        fname += '.csv'
        if mode == 'lexware':
            self.payments.to_csv(fname, date_format='%d.%m.%Y',
                                 index=False, line_terminator='\r\n')
        else:
            self.payments.to_csv(fname, index=False)
        _log.info("Wrote %s", fname)

    def to_json(self, fname):
        """Create a json export from bunq data"""
        fname += '.json'
        self.payments.to_json(fname, orient='records', date_format='iso')
        _log.info("Wrote %s", fname)

    def __len__(self):
        return len(self.payments)


class Balances():
    """
    represent balances of of all active accounts
    """
    def __init__(self):
        pagination = client.Pagination()
        pagination.count = 50

        all_accounts = generated.endpoint.MonetaryAccountBank.list(
            pagination.url_params_count_only).value

        self.balances = {
            aacc.description: (aacc.balance.currency, aacc.balance.value)
            for aacc in (monetary_account_bank
                         for monetary_account_bank in all_accounts
                         if monetary_account_bank.status == "ACTIVE")}

    def __repr__(self):
        return "\n".join((f"{k}: {v[1]} {v[0]}"
                          for k, v in self.balances.items()))


def _export(fname, payments, user, mode):
    """Do the exporting in various formats"""
    if fname is None:
        fname = 'bunq_%s' % user.id_
    payments.to_csv(fname, mode)
    payments.to_json(fname)


def _print_status(payments):
    """print some status info to stdout"""
    print(payments)
    print(Balances())


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
                        format="[%(levelname)-7s] %(message)s",
                        stream=sys.stderr)
    # connect
    _setup_context(args.conf)

    user = generated.endpoint.User.get().value.get_referenced_object()
    payments = Payments(_get_all_payments(args.payments))
    _export(args.outfile, payments, user, args.mode)
    _print_status(payments)

    # disconnect
    context.BunqContext.api_context().save(args.conf)


if __name__ == '__main__':
    main()
