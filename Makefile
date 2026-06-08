.PHONY: tos \
        env-backend env-frontend envs \
        install-backend install-frontend install \
        run-backend run-frontend \
        up down logs \
        crawl \
        freeze-backend freeze-frontend freeze \
        delete-backend delete-frontend delete-envs \
        grader-load-esonero grader-load-final \
        test-esonero test-final test-final-report

CONDA ?= $(shell which conda)

# ─── Conda ToS ───────────────────────────────────────────────────────────────

# Run once before creating environments.
tos:
	$(CONDA) tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
	$(CONDA) tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r

# ─── Environment setup ───────────────────────────────────────────────────────

env-backend:
	$(CONDA) create -n creeping-crawler-backend python=3.11 -y
	$(CONDA) run -n creeping-crawler-backend pip install -r backend/requirements.txt
	$(CONDA) run -n creeping-crawler-backend python -m playwright install --with-deps chromium

env-frontend:
	$(CONDA) create -n creeping-crawler-frontend python=3.11 -y
	$(CONDA) run -n creeping-crawler-frontend pip install -r frontend/requirements.txt

envs: env-backend env-frontend

# ─── Dependency install (existing envs) ──────────────────────────────────────

install-backend:
	$(CONDA) run -n creeping-crawler-backend pip install -r backend/requirements.txt
	$(CONDA) run -n creeping-crawler-backend python -m playwright install --with-deps chromium

install-frontend:
	$(CONDA) run -n creeping-crawler-frontend pip install -r frontend/requirements.txt

install: install-backend install-frontend

# ─── Run ─────────────────────────────────────────────────────────────────────

# Backend API on port 8003.
run-backend:
	cd backend && $(CONDA) run --no-capture-output -n creeping-crawler-backend uvicorn src.server:app --host 0.0.0.0 --port 8003

# Frontend UI on port 8004.
run-frontend:
	cd frontend && $(CONDA) run --no-capture-output -n creeping-crawler-frontend uvicorn src.app:app --host 0.0.0.0 --port 8004

# ─── Docker Compose ──────────────────────────────────────────────────────────

# Pass a service name as positional arg to target a single container.
#   make up                # start all services in background
#   make up mariadb        # start only mariadb
#   make logs backend      # follow logs of the backend
#   make down              # stop and remove all services
#   make down ollama       # stop and remove only ollama
_DC_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))

up:
	docker compose up --build -d $(_DC_ARGS)

down:
	docker compose down $(_DC_ARGS)

logs:
	docker compose logs -f $(_DC_ARGS)

# ─── Crawl ───────────────────────────────────────────────────────────────────

# Crawl gold standard URLs into gs_results/.
# Pass args after --: make crawl -- --domain www.xe.com --update-json
crawl:
	cd backend && $(CONDA) run --no-capture-output -n creeping-crawler-backend python crawl_gs.py $(_DC_ARGS)

# Silences the extra "targets" Make sees when args are passed positionally.
%:
	@:

# ─── Freeze ──────────────────────────────────────────────────────────────────

freeze-backend:
	$(CONDA) run -n creeping-crawler-backend pip freeze | grep -v '@ file://' > backend/requirements.txt

freeze-frontend:
	$(CONDA) run -n creeping-crawler-frontend pip freeze | grep -v '@ file://' > frontend/requirements.txt

freeze: freeze-backend freeze-frontend

# ─── Graders ─────────────────────────────────────────────────────────────────

# Esonero (Lab Exam 1).
GRADER_ESONERO_IMAGE ?= lab-grader-esonero.tar.gz
GRADER_ESONERO_TAG   := lab-grader-esonero-1:1.0.1

# Final project.
GRADER_FINAL_IMAGE   ?= lab-grader-progetto-finale.tar.gz
GRADER_FINAL_TAG     := lab-grader-progetto-finale:1.0.4

STUDENT_ID ?=

grader-load-esonero:
	docker load -i $(GRADER_ESONERO_IMAGE)

grader-load-final:
	docker load -i $(GRADER_FINAL_IMAGE)

# Usage: make test-esonero STUDENT_ID=<your_student_id>
test-esonero:
ifndef STUDENT_ID
	$(error STUDENT_ID is not set. Usage: make test-esonero STUDENT_ID=<your_student_id>)
endif
	docker run --rm --name creeping-crawler-grader-esonero --network host $(GRADER_ESONERO_TAG) $(STUDENT_ID)

# Usage: make test-final STUDENT_ID=<your_student_id>
test-final:
ifndef STUDENT_ID
	$(error STUDENT_ID is not set. Usage: make test-final STUDENT_ID=<your_student_id>)
endif
	docker run --rm --name creeping-crawler-grader-final --network host $(GRADER_FINAL_TAG) $(STUDENT_ID)

# Writes a JSON report to ./output/report.json.
# Usage: make test-final-report STUDENT_ID=<your_student_id>
test-final-report:
ifndef STUDENT_ID
	$(error STUDENT_ID is not set. Usage: make test-final-report STUDENT_ID=<your_student_id>)
endif
	mkdir -p output
	docker run --rm --name creeping-crawler-grader-final --network host \
		-v "$(CURDIR)/output:/output" \
		$(GRADER_FINAL_TAG) $(STUDENT_ID) --machine -o /output/report.json

# ─── Cleanup ─────────────────────────────────────────────────────────────────

delete-backend:
	$(CONDA) remove -n creeping-crawler-backend --all -y

delete-frontend:
	$(CONDA) remove -n creeping-crawler-frontend --all -y

delete-envs: delete-backend delete-frontend
