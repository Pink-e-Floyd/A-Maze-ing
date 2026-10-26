PYTHON := python3
CONFIG := config.txt
MYPY_FLAGS := --warn-return-any --warn-unused-ignores --ignore-missing-imports \
			--disallow-untyped-defs --check-untyped-defs

install:
	$(PYTHON) -m pip install -r requirements-dev.txt

run:
	$(PYTHON) a_maze_ing.py $(CONFIG)

debug:
	$(PYTHON) -m pdb a_maze_ing.py $(CONFIG)

clean:
	rm -rf .mypy_cache .pytest_cache build dist *.egg-info
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +

lint:
	flake8 .
	mypy . $(MYPY_FLAGS)

lint-strict:
	flake8 .
	mypy . --strict

build:
	$(PYTHON) -m build
	cp dist/mazegen-*.whl .

.PHONY: install run debug clean lint lint-strict build