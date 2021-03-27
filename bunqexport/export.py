#!/usr/bin/env python -W ignore
# -*- coding: utf-8 -*-
""" Connect to bunq api and create a csv/json file with all latest payments for
every active account.

- 'mode' lexware is to support importing the csv into Lexware Finazmanger via
  'Datei / Export/Import / Datenimport... / Umsätze', or even better with the
  Vorlagen.dat (FM does not support isodates)

"""

import argparse
import json
import logging
import sys

import pandas

import bunq
import bunq.sdk.context.api_context
import bunq.sdk.context.bunq_context
from bunq.sdk.model import generated

__all__ = ['main', 'payments_as_dataframe']

_log = logging.getLogger(__name__)  # pylint: disable=invalid-name


def _setup_context(conf):
    """setup the context (login, etc) to work with bunq api"""
    _log.info('Using conf: %s', conf)
    api_context = bunq.sdk.context.api_context.ApiContext.restore(conf)
    api_context.ensure_session_active()
    api_context.save(conf)
    bunq.sdk.context.bunq_context.BunqContext.load_api_context(api_context)


def _iter_all_payments(account_id, count=200):
    """Iterate over all payments of 'account_id' with steps of 'count'."""
    result = None

    while result is None or result.value:
        if result is None:
            pagination = bunq.Pagination()
            pagination.count = count  # maximum number
            params = pagination.url_params_count_only
        elif result.pagination.has_previous_page():
            params = result.pagination.url_params_previous_page
        else:
            break

        result = generated.endpoint.Payment.list(
            params=params, monetary_account_id=account_id
        )
        _log.info('found %d while fetching last %d Payments for account %s',
                  len(result.value), count, account_id)

        if not result.value:
            break

        for payment in result.value:
            yield payment


def _get_all_payments(count, account_id=None):
    """Fetch all Payments wie bunq api in bunq_sdk format"""
    payments_gen = _iter_all_payments(account_id, 200)
    result = []
    for _ in range(count):
        try:
            result.append(next(payments_gen))
        except StopIteration:
            break
    return result


class Payments():
    """
    Abstraction over bunq payments using a pandas dataframe

    payments are served in json
    """

    def __init__(self, payments):
        self.payments = pandas.json_normalize(json.loads(payments))
        self.payments['created'] = pandas.to_datetime(self.payments['created'])
        self.payments['updated'] = pandas.to_datetime(self.payments['updated'])
        self.payments['description'] = \
            self.payments['description'].str.replace(r'\n', ' ')

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

    def to_csv(self, path_or_buf, mode=None):
        """Create a csv export from bunq data"""
        self.payments.to_csv(
            path_or_buf,
            date_format='%d.%m.%Y' if mode == 'lexware' else None,
            index=False,
            line_terminator='\n' if sys.platform == 'win32' else '\r\n')

    def to_json(self, path_or_buf):
        """Create a json export from flattened (depth=1) bunq data"""
        self.payments.to_json(path_or_buf, orient='records', date_format='iso')

    def __len__(self):
        return len(self.payments)

    @classmethod
    def fetch_account(cls, account_id, count):
        """Fetch 'count' payments from 'account_id'."""
        payments = _get_all_payments(count, account_id)
        payments_as_json = (p.to_json() for p in reversed(payments))
        data = '[' + ','.join(payments_as_json) + ']'
        return Payments(data)


class Accounts():  # pylint: disable=too-few-public-methods
    """
    represent balances of of all active accounts
    """

    def __init__(self):
        pagination = bunq.Pagination()
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
    payments.to_csv(fname + '.csv', mode)
    _log.info('Wrote %s', fname + '.csv')
    payments.to_json(fname + '.json')
    _log.info('Wrote %s', fname + '.json')


def payments_as_dataframe(
        conf: str = 'bunq-sandbox.conf', payments_per_account: int = 200):
    """Fetch payments from all accounts as pandas.DataFrame."""
    _setup_context(conf)
    accounts = Accounts()
    dfs = [
        Payments.fetch_account(account_id, payments_per_account).payments
        for account_id, account_name in accounts.ids()
    ]
    combined_df = pandas.concat(dfs)
    for col in ('amount.value', 'balance_after_mutation.value'):
        combined_df[col] = combined_df[col].astype(float)
    return combined_df.sort_values('created', ascending=False)


def main():
    """main entrypoint"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--conf', default='bunq-sandbox.conf',
                        help='api config file')
    parser.add_argument('--outfile', '-o', default=None,
                        help='name of the export csv file')
    parser.add_argument('--payments', default=200, type=int,
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
        payments = Payments.fetch_account(account_id, args.payments)
        _export(args.outfile, payments, user, account_name, args.mode)
        print(payments)

    print(accounts)

    # disconnect
    bunq.sdk.context.bunq_context.BunqContext.api_context().save(args.conf)


if __name__ == '__main__':
    main()
