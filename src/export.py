#!/usr/bin/env python -W ignore
import argparse
import collections
import csv
import datetime
import json
import logging
import sys

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


def _flatten(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(_flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return collections.OrderedDict(items)


def _fmt_date(dateval, fmt):
    if not dateval:
        return ""
    # FIXME: not with py36 :-(
    # dt = datetime.datetime.fromisoformat(dateval)
    dt = datetime.datetime.strptime(dateval[:10], "%Y-%m-%d")
    return dt.strftime(fmt)


def _exportcsv(fname, payments, mode):
    # Create a csv export from bunq data
    first = True
    with open(fname, 'w', newline='') as csvfile:
        for p in reversed(payments):
            flatp = _flatten(json.loads(p.to_json()))
            if first:
                writer = csv.DictWriter(csvfile, fieldnames=flatp.keys())
                writer.writeheader()
                first = False
            if mode == 'lexware':
                # FM does not understand ISO Format Timestamps, needs
                # DD.MM.YYYY
                flatp['created'] = _fmt_date(flatp['created'], "%d.%m.%Y")
                flatp['updated'] = _fmt_date(flatp['updated'], "%d.%m.%Y")
            _log.info('%s %7s %3s %-8s %-10s %-40s %s', flatp['created'],
                      flatp['amount_value'], flatp['amount_currency'],
                      flatp['sub_type'], flatp['type'],
                      
                      flatp['counterparty_alias_name'], flatp['description'])
            #for k,v in flatp.items():
            #    print (k, v)
            writer.writerow(flatp)
    _log.info("Wrote %s", fname)


def main(fname, conf, no_of_payments, mode):
    _log.info("Using conf: %s", conf)
    _setup_context(conf)
    payments = _get_all_payments(no_of_payments)
    user = generated.endpoint.User.get().value.get_referenced_object()
    if fname is None:
        fname = '%s.csv' % user.id_
    _log.info(f'{len(payments)} Payments for {user.display_name}')
    _exportcsv(fname, payments, mode)
    _log.info(f'Balance: {payments[0].balance_after_mutation.currency} {payments[0].balance_after_mutation.value}')
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
