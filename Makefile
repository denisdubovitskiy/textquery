.PHONY: install-deps
install-deps:
	poetry install

.PHONY: test
test: install-deps
	PYTHONPATH=. poetry run py.test --verbose