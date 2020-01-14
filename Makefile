# -*- mode: Makefile; encoding: utf-8 -*-
.PHONY:upload all pre-commit tests upload

all: tests pre-commit

pre-commit:
	pre-commit run --all-files

tests:
	nosetests bunqexport

upload:
	python setup.py sdist
	twine upload dist/*
