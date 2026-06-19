.PHONY: install run test bless

install:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt -r requirements-dev.txt
	cd frontend && npm install

run:
	@trap 'kill 0' EXIT; \
	.venv/bin/uvicorn app.main:app --reload & \
	cd frontend && npm run dev

test:
	PYTHONPATH=. .venv/bin/pytest

bless:
	PYTHONPATH=. UPDATE_SNAPSHOT=1 .venv/bin/pytest
