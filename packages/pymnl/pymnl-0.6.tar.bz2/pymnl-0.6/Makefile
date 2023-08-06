# -*- coding: utf-8 -*-
#
# Makefile for pymnl
#
# Copyright 2015 Sean Robinson <robinson@tuxfamily.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# `GNU General Public License <LICENSE.GPL.html>`_ for more details.
#

# Binaries needed in this file...
COVERAGE2=coverage-py2.7
COVERAGE3=coverage-py3.4
PEP8=pep8-py3.4
PYFLAKES=pyflakes-py3.4
PYTHON2=python2
PYTHON3=python3
SHELL=/bin/sh

package = pymnl

TOPDIR := $(CURDIR)

VERSION = $(shell cat $(TOPDIR)/docs/VERSION)

TESTCASES = pymnl.tests.nlsocket,pymnl.tests.attributes,pymnl.tests.message,pymnl.tests.genl

.PHONY: targets clean coverage doc-clean doc-html help \
	pep8 pep-verbose pyflakes realclean sdist test

targets:
	@echo "Available make targets:"
	@echo "    clean        - remove caches and reports (e.g. coverage)"
	@echo "    coverage     - generate a code coverage report"
	@echo "    doc-clean    - remove generated HTML documentation"
	@echo "    doc-html     - generate HTML documentation"
	@echo "    pep8         - check entire project for PEP8 compliance"
	@echo "    pep8-verbose - include many details about PEP8 check"
	@echo "    pyflakes     - statically analyze entire project for common errors"
	@echo "    realclean    - remove all generated content"
	@echo "    test         - run unit tests"
	@echo ""

clean:
	rm -fr tmp/ dist/ build/ htmlcov/ MANIFEST
	rm -fr `find $(TOPDIR) -type f -a -name "*.pyc"`
	rm -fr `find $(TOPDIR) -type d -a -name "__pycache__"`
	@which $(COVERAGE2) > /dev/null 2>&1 && $(COVERAGE2) erase
	@which $(COVERAGE3) > /dev/null 2>&1 && $(COVERAGE3) erase

coverage:
	# Python 2 code coverage
	@which $(COVERAGE2) > /dev/null 2>&1 || \
		(echo "Code coverage for Python 2 not found" && exit 1)
	PYTHONPATH=$(TOPDIR) $(COVERAGE2) run --parallel-mode --branch \
		--omit="*testcommand*" \
		./setup.py test --test-list $(TESTCASES) --test-verbose
	# Python 3 code coverage
	@which $(COVERAGE3) > /dev/null 2>&1 || \
		(echo "Code coverage for Python 3 not found" && exit 1)
	PYTHONPATH=$(TOPDIR) $(COVERAGE3) run --parallel-mode --branch \
		--omit="*testcommand*" \
		./setup.py test --test-list $(TESTCASES) --test-verbose
	$(COVERAGE2) combine
	$(COVERAGE2) html

doc-clean:
	( cd docs && make clean )

doc-html:
	( cd docs && make html )
	cp -a ./docs/source/_static/haiku.css ./docs/build/html/_static/haiku.css
	$(MAKE) clean

pep8:
	$(PEP8) --statistics pymnl/ examples/

pep8-verbose:
	$(PEP8) --show-source --show-pep8 --statistics pymnl/ examples/

pyflakes:
	$(PYFLAKES) pymnl/ examples/

realclean: doc-clean clean

sdist:	realclean doc-html $(TOPDIR)/dist/${package}-$(VERSION).tar.bz2.sha256 $(TOPDIR)/dist/${package}-$(VERSION).tar.bz2.sign

test:
	PYTHONPATH=$(TOPDIR) $(PYTHON2) ./setup.py test \
		--test-list $(TESTCASES) --test-verbose
	PYTHONPATH=$(TOPDIR) $(PYTHON3) ./setup.py test \
		--test-list $(TESTCASES) --test-verbose

$(TOPDIR)/dist/${package}-$(VERSION).tar.bz2:
	PYTHONPATH=$(TOPDIR) $(PYTHON2) ./setup.py sdist --force-manifest --formats=bztar

$(TOPDIR)/dist/${package}-$(VERSION).tar.bz2.sha256: $(TOPDIR)/dist/${package}-$(VERSION).tar.bz2
	cd $(TOPDIR)/dist && \
		sha256sum ${package}-$(VERSION).tar.bz2 \
			> ${package}-$(VERSION).tar.bz2.sha256

$(TOPDIR)/dist/${package}-$(VERSION).tar.bz2.sign: $(TOPDIR)/dist/${package}-$(VERSION).tar.bz2
	cd $(TOPDIR)/dist && \
		gpg --detach-sign -a --output \
			${package}-$(VERSION).tar.bz2.asc \
			${package}-$(VERSION).tar.bz2
	cd $(TOPDIR)/dist && \
		chmod 644 $(TOPDIR)/dist/${package}-$(VERSION).tar.bz2.asc
	cd $(TOPDIR)/dist && \
		gpg --verify $(TOPDIR)/dist/${package}-$(VERSION).tar.bz2.asc
