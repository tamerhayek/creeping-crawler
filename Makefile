.PHONY: env-backend env-frontend envs delete-backend delete-frontend delete-envs tos freeze-backend freeze-frontend freeze run-backend run-frontend

CONDA ?= $(shell which conda)

tos:
	$(CONDA) tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
	$(CONDA) tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r

env-backend:
	$(CONDA) create -n crawl4ai-backend python=3.11 -y
	$(CONDA) run -n crawl4ai-backend pip install -r backend/requirements.txt
	$(CONDA) run -n crawl4ai-backend python -m playwright install --with-deps chromium

env-frontend:
	$(CONDA) create -n crawl4ai-frontend python=3.11 -y
	$(CONDA) run -n crawl4ai-frontend pip install -r frontend/requirements.txt

envs: env-backend env-frontend

install-backend:
	$(CONDA) run -n crawl4ai-backend pip install -r backend/requirements.txt
	$(CONDA) run -n crawl4ai-backend python -m playwright install --with-deps chromium

install-frontend:
	$(CONDA) run -n crawl4ai-frontend pip install -r frontend/requirements.txt

install: install-backend install-frontend

delete-backend:
	$(CONDA) remove -n crawl4ai-backend --all -y

delete-frontend:
	$(CONDA) remove -n crawl4ai-frontend --all -y

delete-envs: delete-backend delete-frontend

freeze-backend:
	$(CONDA) run -n crawl4ai-backend pip freeze | grep -v '@ file://' > backend/requirements.txt

freeze-frontend:
	$(CONDA) run -n crawl4ai-frontend pip freeze | grep -v '@ file://' > frontend/requirements.txt

freeze: freeze-backend freeze-frontend

run-backend:
	cd backend && $(CONDA) run --no-capture-output -n crawl4ai-backend uvicorn src.server:app --host 0.0.0.0 --port 8003

run-frontend:
	cd frontend && $(CONDA) run --no-capture-output -n crawl4ai-frontend uvicorn src.app:app --host 0.0.0.0 --port 8004
