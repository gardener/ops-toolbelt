PYTHON := python3
VENV_DIR := .venv
VENV_BIN := $(VENV_DIR)/bin
VENV_PYTHON := $(VENV_BIN)/$(PYTHON)
red=\033[0;31m
color_reset=\033[0m

# Check if venv is loaded before doing any changes
ensure-venv:
	@if [ ! -d ".venv" ]; then \
		echo "$(red)Virtual environment not found. Please run:$(color_reset) make venv"; \
		$(MAKE) venv-update; \
	fi
	@if [ -z "$$VIRTUAL_ENV" ]; then \
		echo "$(red)Activate yout venv with:$(color_reset) source .venv/bin/activate"; \
		exit 1; \
	fi

ensure-shellcheck:
	@command -v shellcheck > /dev/null || { echo "shellcheck is not installed. Please install shellcheck"; exit 1; }
	@command -v shellcheck-sarif > /dev/null || { echo "shellcheck-sarif is not installed. Please install shellcheck-sarif"; exit 1; }

venv-build:
	@$(PYTHON) -m venv .venv
	@echo "Virtual environment created. Run $(red)'source .venv/bin/activate'$(color_reset) to activate it."

venv-update:
	@source .venv/bin/activate; pip install --upgrade pip; pip install -r requirements.txt

venv: venv-update

verify: ensure-venv ensure-shellcheck
	@.ci/verify-bandit
	@.ci/verify-shellcheck

build: ensure-venv
	@.ci/build

build-image: build
	@docker build -t ops-toolbelt -f generated_dockerfiles/ops-toolbelt.dockerfile . --no-cache

validate: ensure-venv
	@$(VENV_PYTHON) generator/validate-tools.py \
            --dockerfile-configs dockerfile-configs/common-components.yaml

