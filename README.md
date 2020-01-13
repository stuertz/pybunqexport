# Bunqexport

After the some discussion in the lexware Finanzmanger forum, it looks
like the authors do not feel the need to integrate bunq into their
application (https://forum.lexware.de/threads/37851/)

Also in the bunq forums, no one seemed to have a prior solution
(https://together.bunq.com/d/24026-lexware-quicken-finanzmanager-import-from-bunq).

So I decided to implement a simple export with python and the bunq
rest API.

## Features

* Connect to bunq (https://www.bunq.com) API with a pregenerated API
  key (see Tinker example: https://github.com/bunq/tinker_python)
* Export payments from bunq as `json` and `csv` into one file per
  account
* support special `csv` format with timestamps in `DD.MM.YYYY` format
  in timstamps, as expected from `Haufe-Lexware Finanzmanger`, when
  mode is `lexware`
* Unit testing using `nose`

## Usage

Install `bunqexport` and generate an export:

```
$ pip install bunqexport
$ bunqexport --conf bunq-production.conf --mode lexware
```
