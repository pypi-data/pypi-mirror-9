#!/bin/sh

export PYTHONPATH=.
flake8 shifty/*.py
nosetests --exe -v -s --nologcapture --cover-inclusive --with-coverage --cover-package=shifty --cover-erase --cover-html-dir=~/.coverage --cover-branches --with-xunit tests
