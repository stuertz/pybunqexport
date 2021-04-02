# Bunqexport 🌈

After the some discussion in the lexware Finanzmanger forum, it looks
like the authors do not feel the need to integrate bunq into their
application (https://forum.lexware.de/threads/37851/)

Also in the bunq forums, no one seemed to have a prior solution
(https://together.bunq.com/d/24026-lexware-quicken-finanzmanager-import-from-bunq).

So I decided to implement a simple export with python and the bunq
rest API.

## Features

- Connect to bunq (https://www.bunq.com) API with a pregenerated API
  key (see Tinker example: https://github.com/bunq/tinker_python)
- Export payments from bunq as `json` and `csv` into one file per
  account
- support special `csv` format with timestamps in `DD.MM.YYYY` format
  in timstamps, as expected from `Haufe-Lexware Finanzmanger`, when
  mode is `lexware`
- Unit testing using `nose`
- Pre-commit checking with `pre-commit`

## Usage

Install `bunqexport` and generate an export:

```
$ pip install bunqexport
$ bunqexport --conf bunq-production.conf --mode lexware
[INFO   ] Using conf: bunq-production.conf
[INFO   ] found XX while fetching last 200 Payments for account XXXXXXX
[INFO   ] Wrote bunq_XXXXXXX_Default.csv
[INFO   ] Wrote bunq_XXXXXXX_Default.json
created    type               counterparty_alias.name                   amount.currency amount.value description
23.12.2019  CHECKOUT_MERCHANT                                      bunq  EUR              200.00                                    bunq account top up
23.12.2019         MASTERCARD                    XXXXXXXXXXXXXXXXXXXXXX  EUR              -16.96               XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
23.12.2019            SAVINGS                               XXXXXXXXXXX  EUR               -0.04
24.12.2019            EBA_SCT                                XXXXXXXXXX  EUR              500.00                                                    ---
27.12.2019            EBA_SCT  PayPal (Europe) S.a.r.l. et Cie., S.C.A.  EUR                0.13                           PAYPAL BEVEILIGINGSMAATREGEL
27.12.2019            EBA_SCT  PayPal (Europe) S.a.r.l. et Cie., S.C.A.  EUR                0.03                           PAYPAL BEVEILIGINGSMAATREGEL
...
```

## Contributing

Any contributions are very welcome.

When contributing to this repository, please first discuss the change
you wish to make via issue with the owners of this repository before
making a change.

### Pull Request Process

1. Ensure any install or build dependencies are removed before the end
   of the layer when doing a build.
2. Document your changes (whereever useful), e.g in `README.md`.
3. Use `pre-commit` hooks by installing `pip install pre-commit` and run `pre-commit install`.

## License

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
