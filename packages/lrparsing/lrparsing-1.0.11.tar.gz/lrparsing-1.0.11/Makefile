#!/usr/bin/make -f
#
# Copyright (c) 2013,2014,2015 Russell Stuart.
# Licensed under GPLv2, or any later version.

DESTDIR ?= /
PYTHON ?= python

.PHONY:	all
all:	doc lrparsing

.PHONY:	lrparsing
lrparsing:
	$(MAKE) --directory lrparsing

.PHONY:	doc
doc:
	$(MAKE) --directory doc

.PHONY:	test
test:	
	$(MAKE) --directory lrparsing $@
	$(MAKE) --directory doc $@

.PHONY:	clean
clean:
	$(MAKE) --directory lrparsing $@
	$(MAKE) --directory doc $@
	rm -rf release build dist MANIFEST .*.sw?

.PHONY:	install
install: install-doc install-lrparsing

.PHONY:	install-doc
install-doc:
	$(MAKE) --directory doc $@

.PHONY:	install-lrparsing
install-lrparsing:
	$(MAKE) --directory lrparsing $@
	$(PYTHON) setup.py install $(DIST_PYFLAGS) --root=$(DESTDIR)

.PHONY: pypi
pypi:
	$(MAKE) release-clean
	$(PYTHON) setup.py register sdist upload --sign --identity=0xE7843A8C

RELEASE_SOURCES = \
	ChangeLog.txt \
	MANIFEST.in \
	Makefile \
	Makefile.release \
	README.txt \
	doc/lrparsing.rst \
	lrparsing.html \
	lrparsing/lrparsing.py \
	lrparsing/test.py \
	setup.py

include Makefile.release

release-project-clean:: clean
