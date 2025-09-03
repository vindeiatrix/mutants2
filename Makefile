.PHONY: smoke test fmt lint

smoke:
	pytest -q tests/smoke

test:
	pytest -q

fmt:
	ruff check --fix .
	black .

lint:
	ruff check .
	black --check .
