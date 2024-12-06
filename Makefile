SHELL := bash

.PHONY: help

# Usage: make help
help:
	@cat Makefile | grep "^# Usage:"

.env:
	@./bin/setup-env-vars.sh

.PHONY: diff refresh up down

# Usage: make diff
diff: .env
	source .env && pulumi preview --cwd infra-as-code/ -s main --diff

# Usage: make refresh
refresh: .env
	source .env && pulumi refresh --cwd infra-as-code/ -s main

# Usage: make up
up: .env
	source .env && pulumi up --cwd infra-as-code/ -s main

# Usage: make down
down: .env
	source .env && pulumi destroy --cwd infra-as-code/ -s main

.PHONY: debug run

debug:
	source .env && poetry run dbt debug --connection

run:
	source .env && poetry run dbt run

.PHONY: pre-commit

# Usage: pre-commit
pre-commit:
	pre-commit
