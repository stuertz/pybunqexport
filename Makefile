# -*- mode: Makefile; coding: utf-8 -*-
.PHONY:upload all pre-commit tests upload

all: tests pre-commit

pre-commit:
	pre-commit run --all-files

tests:
	nosetests --with-coverage --cover-package bunqexport bunqexport

upload:
	python3 setup.py sdist
	twine upload dist/*
