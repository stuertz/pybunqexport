# -*- mode: Makefile; coding: utf-8 -*-
.PHONY:upload all pre-commit tests upload

all: tests pre-commit

pre-commit:
	pre-commit run --all-files

tests:
	nosetests --with-coverage --cover-package bunqexport bunqexport

dist:
	rm -rf dist
	python3 setup.py sdist
	python3 setup.py bdist_egg
	python3 setup.py bdist_wheel

upload: dist
	twine upload dist/*
