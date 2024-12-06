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
	source .env && pulumi preview -s main --diff

# Usage: make refresh
refresh: .env
	source .env && pulumi refresh -s main

# Usage: make up
up: .env
	source .env && pulumi up -s main

# Usage: make down
down: .env
	source .env && pulumi destroy -s main

.PHONY: pre-commit

# Usage: pre-commit
pre-commit:
	pre-commit
