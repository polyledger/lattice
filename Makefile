clean-pyc:
	find . -name "*.pyc" -exec rm -f {} \;

clean-build:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info

init:
	pip install -r requirements.txt

test: clean-pyc
	python3 -m unittest discover --verbose --start-directory tests -b

.PHONY: clean-pyc clean-dist init test

help:
	@echo "clean-pyc"
	@echo "    Remove python artifacts."
	@echo "clean-build"
	@echo "    Remove build artifacts."
	@echo "init"
	@echo "    Install module dependencies."
	@echo "test"
	@echo "    Run test suite."
