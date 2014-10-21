all: pylint test

pylint:
	flake8 -v .
test:
	nosetests --with-coverage --cover-erase --cover-package=index,systime

.PHONY: pylint test
