.PHONY: setup fmt lint type test all
setup:
	uv sync
	pre-commit install
fmt: 
	uv run ruff format && uv run black src tests
lint:
	uv run ruff check src tests
type:
	uv run mypy src
test:
	uv run pytest -q
all: fmt lint type test