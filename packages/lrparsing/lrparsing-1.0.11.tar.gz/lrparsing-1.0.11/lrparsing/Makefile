#!/usr/bin/make -f
#
# Copyright (c) 2013,2014,2015 Russell Stuart.
# Licensed under GPLv2, or any later version.

all:

.PHONY: install install-lrparsing
install: install-lrparsing
install-lrparsing:

.PHONY: clean
clean:
	rm -rf coverage .coverage *.py[co] .*.sw? __pycache__

.PHONY: test
test:	
	$(MAKE) clean
	python3 test.py
	$(MAKE) clean
	mkdir -p coverage
	python-coverage run test.py
	rm -f coverage/*
	python-coverage html -d coverage
	@python-coverage report  --include lrparsing.py | grep --silent ' 100%$$' || { echo -n "Test coverage is not 100%: "; python-coverage report  --include lrparsing.py | grep '[0-9]\+%$$'; exit 1; }
	pep8 lrparsing.py
	pep8 --ignore=E501,E241 test.py
