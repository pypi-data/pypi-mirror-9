# Compatibility for us old-timers.

# Note: This makefile include remake-style target comments.
# These comments before the targets start with #:
# remake --tasks to shows the targets and the comments

PHONY=check check-full check3 check-short check-short2 check-short3 clean dist distclean test
GIT2CL ?= git2cl
PYTHON ?= python
PYTHON3 ?= python3

#: the default target - same as running "check"
all: check

#: Run all tests with several Python versions via tox
check-full:
	tox

#: Run all tests with several Python versions via tox, minimum output
check-full-short:
	tox -- --quiet | \
  $(PYTHON) ./make-check-filter.py

#: Run tests (one version of Python)
check:
	$(PYTHON) ./setup.py nosetests

check-short:
	$(PYTHON) ./setup.py nosetests --quiet | \
	$(PYTHON) ./make-check-filter.py
#
# check-short3:
# 	$(PYTHON3) ./setup.py nosetests --quiet | \
# 	$(PYTHON3) ./make-check-filter.py

#: Clean up temporary files
clean:
	$(PYTHON) ./setup.py $@

#: Create source (tarball) and binary (egg) distribution
dist: README.rst
	$(PYTHON) ./setup.py sdist bdist

#: Create source tarball
sdist: README.rst
	$(PYTHON) ./setup.py sdist

#: Create binary egg distribution
bdist_egg: README.rst
	$(PYTHON) ./setup.py bdist_egg

#: Convert README.md to README.rst for PyPI
README.rst: README.md
	pandoc --to=rst README.md  > README.rst

README.txt: README.md
	pandoc --to=plain README.md  > README.text

# It is too much work to figure out how to add a new command to distutils
# to do the following. I'm sure distutils will someday get there.
DISTCLEAN_FILES = build dist *.egg-info *.pyc *.so py*.py

#: Remove ALL dervied files
distclean: clean
	-rm -fr $(DISTCLEAN_FILES) || true

#: Install package locally
install:
	$(PYTHON) ./setup.py install

#: Same as 'check' target
test: check

rmChangeLog:
	rm ChangeLog || true

#: Create a ChangeLog from git via git log and git2cl
ChangeLog: rmChangeLog
	git log --pretty --numstat --summary | $(GIT2CL) >$@

.PHONY: $(PHONY)
