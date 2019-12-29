#!/usr/bin/env python -W ignore
import argparse
import collections
import csv
import datetime
import json
import logging
import sys

import pandas

from bunq.sdk import client
from bunq.sdk import context
from bunq.sdk.model import generated
"""
Connect to bunq api and create a csv file with all latest payments.

'mode' lexware is to support importing the csv into Lexware
Finazmanger via 'Datei / Export/Import / Datenimport... / Umsätze', or
even better with the Vorlagen.dat (FM does not support isodates)

"""

__all__ = ['main']

_log = logging.getLogger(__name__)


def _setup_context(conf):
    api_context = context.ApiContext.restore(conf)
    api_context.ensure_session_active()
    api_context.save(conf)
    context.BunqContext.load_api_context(api_context)


def _get_all_payments(count):
    pagination = client.Pagination()
    pagination.count = count
    return generated.endpoint.Payment.list(
        params=pagination.url_params_count_only).value


class Payments():
    def __init__(self, payments):
        data = (json.loads(p.to_json()) for p in reversed(payments))
        self.payments = pandas.io.json.json_normalize(data)

    @classmethod
    def fmt_date(cls, dateval, fmt):
        if not dateval:
            return ""
        # FIXME: not with py36 :-(
        # dt = datetime.datetime.fromisoformat(dateval)
        dt = datetime.datetime.strptime(dateval[:10], "%Y-%m-%d")
        return dt.strftime(fmt)

    def log(self):
        _log.info("\n%s", self.payments)

    def csv(self, fname, mode):
        # Create a csv export from bunq data
        fname += '.csv'
        with open(fname, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.payments.columns.values)
            writer.writeheader()
            for _, row in self.payments.iterrows():
                if mode == 'lexware':
                    # FM does not understand ISO Format Timestamps, needs
                    # DD.MM.YYYY
                    row['created'] = self.fmt_date(row['created'], "%d.%m.%Y")
                    row['updated'] = self.fmt_date(row['updated'], "%d.%m.%Y")
                writer.writerow(dict(row.items()))
        _log.info("Wrote %s", fname)

    def json(self, fname):
        # Create a csv export from bunq data
        fname += '.json'
        with open(fname, 'w', newline='') as jsonfile:
            json.dump([dict(row) for _, row in self.payments.iterrows()],
                      jsonfile)
        _log.info("Wrote %s", fname)

    def __len__(self):
        return len(self.payments)


def balances():
    pagination = client.Pagination()
    pagination.count = 50

    all_accounts = generated.endpoint.MonetaryAccountBank.list(
        pagination.url_params_count_only).value

    for aa in (monetary_account_bank
               for monetary_account_bank in all_accounts
               if monetary_account_bank.status == "ACTIVE"):
        _log.info(f"Balance: {aa.description} {aa.balance.currency} "
                  f"{aa.balance.value}")


def main(fname, conf, no_of_payments, mode):
    _log.info("Using conf: %s", conf)
    _setup_context(conf)
    user = generated.endpoint.User.get().value.get_referenced_object()
    if fname is None:
        fname = '%s' % user.id_
    payments = Payments(_get_all_payments(no_of_payments))
    _log.info(f'{len(payments)} Payments for {user.display_name}')
    payments.log()
    payments.csv(fname, mode)
    payments.json(fname)
    balances()
    context.BunqContext.api_context().save(conf)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--conf', default='bunq-sandbox.conf',
                        help='api config file')
    parser.add_argument('--outfile', '-o', default=None,
                        help='name of the export csv file')
    parser.add_argument('--payments', default=50,
                        help='Number of payments')
    parser.add_argument('--verbose', '-v', default=False, action='store_true')
    parser.add_argument('--mode', choices=['raw', 'lexware'], default='raw')

    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="[%(levelname)-7s] %(message)s",
                        stream=sys.stderr)
    main(args.outfile, args.conf, args.payments, args.mode)
