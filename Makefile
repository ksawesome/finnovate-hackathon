.PHONY: install lint format type-check test run

install:
	conda env update -f environment.yml --prune

lint:
	ruff check .

format:
	black .
	isort .

type-check:
	mypy src/

test:
	pytest --cov=src --cov-report=html

run:
	streamlit run src/app.py