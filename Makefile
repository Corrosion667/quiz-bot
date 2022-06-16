install:
	poetry install --no-root
	mypy --install-types --non-interactive

full-install:
	pip3 install --user poetry==1.2.0b2
	poetry config virtualenvs.in-project true
	make install

lint:
	poetry run flake8 bots
	poetry run mypy bots