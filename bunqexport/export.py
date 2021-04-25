#!/usr/bin/env python -W ignore
# -*- coding: utf-8 -*-

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
from typing import Optional

import bunq
import bunq.sdk.context.api_context
import bunq.sdk.context.bunq_context
import pandas
from bunq.sdk.model import generated

__all__ = ["main", "payments_as_dataframe"]

_log = logging.getLogger(__name__)  # pylint: disable=invalid-name


def _setup_context(conf):
    """setup the context (login, etc) to work with bunq api"""
    _log.info("Using conf: %s", conf)
    api_context = bunq.sdk.context.api_context.ApiContext.restore(conf)
    api_context.ensure_session_active()
    api_context.save(conf)
    bunq.sdk.context.bunq_context.BunqContext.load_api_context(api_context)


def _iter_all_payments(account_id, count=200, present_ids=None):
    """Iterate over all payments of 'account_id' with steps of 'count'."""
    result = None
    present_ids = present_ids or set()
    should_stop = False
    while (result is None or result.value) and not should_stop:
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
        _log.info(
            "found %d while fetching last %d Payments for account %s",
            len(result.value),
            count,
            account_id,
        )

        if not result.value:
            break

        for payment in result.value:
            if payment._id_ in present_ids:
                should_stop = True
                break
            yield payment


def _get_all_payments(count, account_id=None, present_ids=None):
    """Fetch all Payments wie bunq api in bunq_sdk format"""
    payments_gen = _iter_all_payments(account_id, 200, present_ids)
    result = []
    for _ in range(count):
        try:
            result.append(next(payments_gen))
        except StopIteration:
            break
    return result


class Payments:
    """
    Abstraction over bunq payments using a pandas dataframe

    payments are served in json
    """

    def __init__(self, payments):
        self.payments = pandas.json_normalize(json.loads(payments))
        if self.payments.size > 0:
            self.payments["created"] = pandas.to_datetime(self.payments["created"])
            self.payments["updated"] = pandas.to_datetime(self.payments["updated"])
            self.payments["description"] = self.payments["description"].str.replace(
                r"\n", " "
            )

    def __repr__(self):
        return self.payments.to_string(
            columns=(
                "created",
                "type",
                "counterparty_alias.name",
                "amount.currency",
                "amount.value",
                "description",
            ),
            show_dimensions=False,
            index=False,
            justify="left",
            formatters={
                "created": lambda x: x.strftime("%d.%m.%Y"),
                "description": lambda x: x.replace("\n", " ").strip(),
            },
        )

    def to_csv(self, path_or_buf, mode=None):
        """Create a csv export from bunq data"""
        self.payments.to_csv(
            path_or_buf,
            date_format="%d.%m.%Y" if mode == "lexware" else None,
            index=False,
            line_terminator="\n" if sys.platform == "win32" else "\r\n",
        )

    def to_json(self, path_or_buf):
        """Create a json export from flattened (depth=1) bunq data"""
        self.payments.to_json(path_or_buf, orient="records", date_format="iso")

    def __len__(self):
        return len(self.payments)

    @classmethod
    def fetch_account(cls, account_id, count, present_ids=None):
        """Fetch 'count' payments from 'account_id'."""
        payments = _get_all_payments(count, account_id, present_ids)
        payments_as_json = (p.to_json() for p in reversed(payments))
        data = "[" + ",".join(payments_as_json) + "]"
        return Payments(data)


class Accounts:  # pylint: disable=too-few-public-methods
    """
    represent balances of of all active accounts
    """

    def __init__(self):
        pagination = bunq.Pagination()
        pagination.count = 50

        all_accounts = generated.endpoint.MonetaryAccountBank.list(
            pagination.url_params_count_only
        ).value

        all_accounts.extend(
            generated.endpoint.MonetaryAccountSavings.list(
                pagination.url_params_count_only
            ).value
        )

        all_accounts.extend(
            generated.endpoint.MonetaryAccountJoint.list(
                pagination.url_params_count_only
            ).value
        )

        self.balances = {
            aacc.id_: (
                aacc.description,
                aacc.balance.currency,
                aacc.balance.value,
                aacc.description,
            )
            for aacc in (
                monetary_account_bank
                for monetary_account_bank in all_accounts
                if monetary_account_bank.status == "ACTIVE"
            )
        }

    def ids(self):
        """
        return tuple of account id and description
        """
        for id_, val in self.balances.items():
            yield id_, val[3]

    def __repr__(self):
        return "\n".join(
            (f"{v[0]} ({k}): {v[2]} {v[1]}" for k, v in self.balances.items())
        )


def _export(fname, payments, user, account_name, mode):
    """Do the exporting in various formats"""
    if fname is None:
        fname = "bunq_%s" % user.id_
    fname += "_%s" % account_name
    payments.to_csv(fname + ".csv", mode)
    _log.info("Wrote %s", fname + ".csv")
    payments.to_json(fname + ".json")
    _log.info("Wrote %s", fname + ".json")


def payments_as_dataframe(
    conf: str = "bunq-sandbox.conf",
    payments_per_account: Optional[int] = None,
    df_old: Optional[pandas.DataFrame] = None,
):
    """Fetch payments from all accounts as pandas.DataFrame.

    If payments_per_account not provided, all payments will be downloaded.

    Optionally pass an incomplete pandas.DataFrame to `df_old` such that
    existing data isn't downloaded again."""
    _setup_context(conf)
    accounts = Accounts()
    if payments_per_account is None:
        payments_per_account = sys.maxsize
    dfs = [] if df_old is None else [df_old]
    for account_id, account_name in accounts.ids():
        if df_old is not None:
            present_ids = set(df_old[df_old["monetary_account_id"] == account_id].id)
        else:
            present_ids = set()
        df_of_account = Payments.fetch_account(
            account_id, payments_per_account, present_ids
        ).payments
        df_of_account["account_name"] = account_name
        dfs.append(df_of_account)
    combined_df = pandas.concat(dfs)
    for col in ("amount.value", "balance_after_mutation.value"):
        combined_df[col] = combined_df[col].astype(float)
    return combined_df.sort_values("created", ascending=False)


def main():
    """main entrypoint"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--conf", default="bunq-sandbox.conf", help="api config file")
    parser.add_argument(
        "--outfile", "-o", default=None, help="name of the export csv file"
    )
    parser.add_argument("--payments", default=200, type=int, help="Number of payments")
    parser.add_argument("--verbose", "-v", default=False, action="store_true")
    parser.add_argument("--mode", choices=["raw", "lexware"], default="raw")

    args = parser.parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="[%(levelname)-7s] %(message)s",
        stream=sys.stderr,
    )
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


if __name__ == "__main__":
    main()
