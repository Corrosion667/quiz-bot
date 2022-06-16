MYPY := poetry run mypy
WPS := poetry run flake8 bots

install:
	poetry install --no-root

full-install:
	pip3 install --user poetry==1.2.0b2
	make install

wps:
	poetry run flake8 bots

mypy:
	$(MYPY) bots

lint:
	make wps
	make mypy

types:
	$(MYPY) --install-types

lint-pipeline:
	make wps
	$(MYPY) --install-types bots --non-interactive
