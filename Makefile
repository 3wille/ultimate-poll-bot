.PHONY: default
default: run

.PHONY: install
install:
	poetry install --develop .

.PHONY: run
run:
	poetry run python main.py

.PHONY: run_api
run_api:
	poetry run python api.py

.PHONY: test
test:
	poetry run pytest

.PHONY:	initdb
initdb:
	poetry run python initdb.py
