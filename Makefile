.PHONY: install install-dev test reproduce clean-venv

install:
	python3 -m pip install --upgrade pip
	python3 -m pip install -e .

test:
	pytest -v

reproduce: install test

clean-venv:
	rm -rf .venv
