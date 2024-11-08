.PHONY: help
help: ## Show this help (usage: make help)
	@echo "Usage: make [target]"
	@echo "Targets:"
	@awk '/^[a-zA-Z0-9_-]+:.*?##/ { \
		helpMessage = match($$0, /## (.*)/); \
		if (helpMessage) { \
			target = $$1; \
			sub(/:/, "", target); \
			printf "  \033[36m%-20s\033[0m %s\n", target, substr($$0, RSTART + 3, RLENGTH); \
		} \
	}' $(MAKEFILE_LIST)


.PHONY: build
build:	## Build project with docker-compose
	docker-compose up --build

.PHONY: up
up:	## Run project with docker-compose
	docker-compose up

.PHONY: down
down: ## Stop project with docker-compose and remove containers and networks
	docker-compose down --remove-orphans | true

.PHONY: db_upgrade
db_upgrade:  ## Upgrade database
	poetry run alembic upgrade head

.PHONY: autogenerate
autogenerate:  ## Generate migration file (usage: make autogenerate msg="migration message")
	poetry run alembic revision --autogenerate -m "$(msg)"

.PHONY: downgrade
downgrade:  ## Downgrade by 1 revision
	poetry run alembic downgrade -1

.PHONY: downgrade_to
downgrade_to:  ## Downgrade to the specific revision (usage: make downgrade_to revision="revision")
	poetry run alembic downgrade "$(revision)"
