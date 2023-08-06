#!/bin/bash

mkdir ./coverage &>/dev/null
# workaround for setting up the codahale metrics in titan - this is a known bug and was fixed, but not merged into titan
nosetests --attr=metrics-setup &>/dev/null
# Run actual coverage tests (python 2 only)
nosetests --attr=unit --attr=concurrency --attr=pooling --with-coverage --cover-erase --cover-package=rexpro --cover-html --cover-xml --cover-min-percentage=80 --cover-html-dir=./coverage/ --cover-xml-file=./coverage/coverage.xml
