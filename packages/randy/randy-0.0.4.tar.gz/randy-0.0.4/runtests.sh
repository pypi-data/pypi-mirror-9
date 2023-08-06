#!/bin/sh

export PYTHONPATH=.
flake8 randy/*.py
nosetests --exe -v -s --nologcapture --with-coverage --cover-package=randy --cover-erase --cover-html-dir=~/.coverage --cover-branches --with-xunit tests
