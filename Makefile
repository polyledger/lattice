clean-pyc:
	find . -name "*.pyc" -exec rm -f {} \;

init:
	pip install -r requirements.txt

test: clean-pyc
	python3 -m unittest discover --verbose --start-directory tests -b

.PHONY: clean-pyc init test

help:
	@echo "init"
	@echo "  Install module dependencies."
	@echo "test"
	@echo "  Run test suite."
