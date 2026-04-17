.PHONY: help build up init down shell logs run1 run2 run3 dashboard clean

help: ## Show this help
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build the tutorial Docker image
	docker compose build

up: ## Start the tutorial dev container
	docker compose up -d
	@echo ""
	@echo "Next steps:"
	@echo "  make init        # one-time: initialize ZenML in this repo"
	@echo "  make run1        # run module 1"
	@echo "  make dashboard   # (host-side) launch the ZenML dashboard"

init: ## One-time: `zenml init` inside the container
	docker compose exec tutorial zenml init

down: ## Stop the dev container
	docker compose down

shell: ## Open a shell in the tutorial container
	docker compose exec tutorial bash

logs: ## Tail container logs
	docker compose logs -f

run1: ## Run module 1 inside the tutorial container
	docker compose exec tutorial python modules/01_first_pipeline/pipeline.py

run2: ## Run module 2 inside the tutorial container
	docker compose exec tutorial python modules/02_artifacts_and_caching/pipeline.py

run3: ## Run module 3 inside the tutorial container
	docker compose exec tutorial python modules/03_stacks_and_deployment/pipeline.py

dashboard: ## Launch the ZenML dashboard on the HOST (needs uv installed locally)
	uv run zenml login --local

clean: ## Stop services and delete .zen/ metadata
	docker compose down
	rm -rf .zen
