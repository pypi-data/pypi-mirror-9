SHELL := /bin/bash

html:
	(cd docs && $(MAKE) html)

testenv:
	pip install -r requirements/common.pip
	pip install -e .

test:
	`which django-admin.py` test --settings=django_openS3.test_settings django_openS3

.PHONY: test