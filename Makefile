PYTHON ?= python3
export PYTHONPATH := src

.PHONY: run test lint clean

run:
	$(PYTHON) -m shellemu $(ARGS)

test:
	$(PYTHON) -m unittest discover -s tests -v

lint:
	$(PYTHON) -m flake8 --max-complexity=10 src tests

clean:
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
