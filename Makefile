SHELL := /usr/bin/env bash
PYTHON := python3
VENV_DIR := .venv
VENV_BIN := $(VENV_DIR)/bin
VENV_PYTHON := $(VENV_BIN)/$(PYTHON)
VENV_PIP := $(VENV_BIN)/pip
APP = 
red=\033[0;31m
color_reset=\033[0m

ensure-venv:
	@if [ ! -d ".venv" ]; then $(MAKE) venv-build; fi

ensure-shellcheck:
	@command -v shellcheck > /dev/null || { echo "shellcheck is not installed. Please install shellcheck"; exit 1; }
	@command -v shellcheck-sarif > /dev/null || { echo "shellcheck-sarif is not installed. Please install shellcheck-sarif"; exit 1; }

venv-build:
	@$(PYTHON) -m venv .venv
	@$(MAKE) venv-update
	@echo "Virtual environment created. Run $(red)'source .venv/bin/activate'$(color_reset) to activate it."

venv-update: ensure-venv
	@$(VENV_PIP) install --upgrade pip; $(VENV_PIP) install -e '.[dev]'

venv: venv-update

verify: ensure-venv ensure-shellcheck
	@VENV_PYTHON=$(VENV_PYTHON) .ci/verify-bandit
	@.ci/verify-shellcheck

validate: venv
	$(VENV_BIN)/generator-validate --dockerfile-config dockerfile-configs/common-components.yaml

build: ensure-venv
	@echo Generating dockerfile
	@VENV_PYTHON=$(VENV_PYTHON) .ci/build

build-image: build
	@docker build -t ops-toolbelt -f generated_dockerfiles/ops-toolbelt.dockerfile . --no-cache

pkg-test: venv
	@$(VENV_BIN)/pytest tests -v --cov=$(APP)
