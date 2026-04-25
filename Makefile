.PHONY: tos \
        env-backend env-frontend envs \
        install-backend install-frontend install \
        run-backend run-frontend \
        crawl \
        freeze-backend freeze-frontend freeze \
        delete-backend delete-frontend delete-envs

CONDA ?= $(shell which conda)

# ─── Conda ToS ───────────────────────────────────────────────────────────────

# Accept Anaconda Terms of Service (run once before creating environments).
tos:
	$(CONDA) tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
	$(CONDA) tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r

# ─── Environment setup ───────────────────────────────────────────────────────

# Create the backend conda environment and install all dependencies.
env-backend:
	$(CONDA) create -n crawl4ai-backend python=3.11 -y
	$(CONDA) run -n crawl4ai-backend pip install -r backend/requirements.txt
	$(CONDA) run -n crawl4ai-backend python -m playwright install --with-deps chromium

# Create the frontend conda environment and install all dependencies.
env-frontend:
	$(CONDA) create -n crawl4ai-frontend python=3.11 -y
	$(CONDA) run -n crawl4ai-frontend pip install -r frontend/requirements.txt

# Create both environments in sequence.
envs: env-backend env-frontend

# ─── Dependency install (existing envs) ──────────────────────────────────────

# Reinstall backend packages into an already-existing environment.
install-backend:
	$(CONDA) run -n crawl4ai-backend pip install -r backend/requirements.txt
	$(CONDA) run -n crawl4ai-backend python -m playwright install --with-deps chromium

# Reinstall frontend packages into an already-existing environment.
install-frontend:
	$(CONDA) run -n crawl4ai-frontend pip install -r frontend/requirements.txt

# Reinstall packages for both environments.
install: install-backend install-frontend

# ─── Run ─────────────────────────────────────────────────────────────────────

# Start the backend API server on port 8003.
run-backend:
	cd backend && $(CONDA) run --no-capture-output -n crawl4ai-backend uvicorn src.server:app --host 0.0.0.0 --port 8003

# Start the frontend UI server on port 8004.
run-frontend:
	cd frontend && $(CONDA) run --no-capture-output -n crawl4ai-frontend uvicorn src.app:app --host 0.0.0.0 --port 8004

# ─── Crawl ───────────────────────────────────────────────────────────────────

# Crawl gold standard URLs and save HTML/markdown results to gs_results/.
# Pass args after --: make crawl -- --domain www.xe.com --update-json
_CRAWL_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
crawl:
	cd backend && $(CONDA) run --no-capture-output -n crawl4ai-backend python crawl_gs.py $(_CRAWL_ARGS)

# Catch-all: silences the extra "targets" Make sees when args are passed via --
%:
	@:

# ─── Freeze ──────────────────────────────────────────────────────────────────

# Snapshot backend dependencies into backend/requirements.txt.
freeze-backend:
	$(CONDA) run -n crawl4ai-backend pip freeze | grep -v '@ file://' > backend/requirements.txt

# Snapshot frontend dependencies into frontend/requirements.txt.
freeze-frontend:
	$(CONDA) run -n crawl4ai-frontend pip freeze | grep -v '@ file://' > frontend/requirements.txt

# Snapshot dependencies for both environments.
freeze: freeze-backend freeze-frontend

# ─── Cleanup ─────────────────────────────────────────────────────────────────

# Remove the backend conda environment.
delete-backend:
	$(CONDA) remove -n crawl4ai-backend --all -y

# Remove the frontend conda environment.
delete-frontend:
	$(CONDA) remove -n crawl4ai-frontend --all -y

# Remove both conda environments.
delete-envs: delete-backend delete-frontend
