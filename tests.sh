#!/bin/bash
pep8 --ignore=E226 archan/checker.py &&
pep8 --ignore=E226 archan/errors.py &&
pep8 --ignore=E226 archan/dsm.py &&
pep8 --ignore=E226,E402 archan/tests.py &&
pyflakes archan/*.py || exit 1
pylint -f colorized -d C0103 archan/*.py || true
