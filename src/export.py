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

_log = logging.getLogger(__name__)


def setup_context(conf):
    api_context = context.ApiContext.restore(conf)
    api_context.ensure_session_active()
    api_context.save(conf)
    context.BunqContext.load_api_context(api_context)


def get_all_payments(count):
    pagination = client.Pagination()
    pagination.count = count
    return generated.endpoint.Payment.list(
        params=pagination.url_params_count_only).value


def flatten(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return collections.OrderedDict(items)


def fmt_date(dateval, fmt):
    # FIXME: not with py36 :-(
    # dt = datetime.datetime.fromisoformat(dateval)
    dt = datetime.datetime.strptime(dateval[:10], "%Y-%m-%d")
    return dt.strftime(fmt)


def exportcsv(fname, payments, mode):
    # Create a csv export from bunq data
    first = True
    user = generated.endpoint.User.get().value.get_referenced_object()
    if fname is None:
        fname = '%s.csv' % user.id_
    _log.info(f'Payments for {user.display_name}')
    with open(fname, 'w', newline='') as csvfile:
        for p in payments:
            flatp = flatten(json.loads(p.to_json()))
            if first:
                writer = csv.DictWriter(csvfile, fieldnames=flatp.keys())
                writer.writeheader()
                first = False
            if mode == 'lexware':
                # FM does not understand ISO Format Timestamps, needs
                # DD.MM.YYYY
                flatp['created'] = fmt_date(flatp['created'], "%d.%m.%Y")
                flatp['updated'] = fmt_date(flatp['updated'], "%d.%m.%Y")
            _log.info('%s %8s %4s %-30s %s', flatp['created'],
                      flatp['amount_value'], flatp['amount_currency'],
                      flatp['counterparty_alias_name'], flatp['description'])
            writer.writerow(flatp)
    _log.info("Wrote %s", fname)


def main(fname, conf, no_of_payments, mode):
    _log.info("Using conf: %s", conf)
    setup_context(conf)
    exportcsv(fname, get_all_payments(no_of_payments), mode)
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
                        stream=sys.stderr)
    main(args.outfile, args.conf, args.payments, args.mode)
