SHELL := /usr/bin/env bash
PYTHON := python3
VENV_DIR = .venv
VENV_BIN = $(VENV_DIR)/bin
VENV_PIP = $(VENV_BIN)/pip
APP = generator
IMAGE_TAG ?= 1877.8
IMAGE_REPO ?= ghcr.io/gardenlinux/gardenlinux
BUILT_IMAGE ?= ops-toolbelt

ifeq ($(shell uname), Darwin)
    OPEN = open
else
    OPEN = xdg-open
endif

TEST_CASES =

red=\033[0;31m
color_reset=\033[0m

.DEFAULT_GOAL := help

.PHONY: help ensure-venv ensure-shellcheck venv-build venv-update venv verify-bandit verify-shellcheck verify validate build build-image pkg-test pkg-test-with-report test reuse

##@ Help

help: ## Display this help.
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Setup

ensure-venv: ## Ensure the virtual environment exists
	@if [ ! -d "$(VENV_DIR)" ]; then $(MAKE) venv-build; fi

venv-build: ## Create a new virtual environment
	@$(PYTHON) -m venv $(VENV_DIR)
	@$(MAKE) venv-update
	@echo "Virtual environment created. Run $(red)'source $(VENV_DIR)/bin/activate'$(color_reset) to activate it."

venv-update: ensure-venv ## Update pip and install dev dependencies
	@$(VENV_PIP) install --upgrade pip; $(VENV_PIP) install -e '.[dev]'

venv: venv-update ## Create or update the virtual environment

##@ Verification

ensure-shellcheck: ## Ensure shellcheck and shellcheck-sarif are available
	@command -v shellcheck > /dev/null || { echo "shellcheck is not installed. Please install shellcheck"; exit 1; }
	@if ! command -v shellcheck-sarif > /dev/null; then cargo install shellcheck-sarif; fi

verify-bandit: ensure-venv ## Run bandit security checks
	@VENV_BIN=$(VENV_BIN) .ci/verify-bandit

verify-shellcheck: ensure-shellcheck ## Run shellcheck on scripts
	@.ci/verify-shellcheck

verify: verify-bandit verify-shellcheck ## Run all verification checks

##@ Build

validate: venv ## Validate the generator configuration
	$(VENV_BIN)/generator-validate --dockerfile-config dockerfile-configs/common-components.yaml

build: ensure-venv ## Generate Dockerfile using the configured base image
	@echo Generating dockerfile
	@$(VENV_BIN)/generator \
		--from-image $(IMAGE_REPO):$(IMAGE_TAG) \
		--dockerfile-config dockerfile-configs/common-components.yaml \
		--dockerfile generated_dockerfiles/$(BUILT_IMAGE).dockerfile

build-image: build ## Build the Docker image from the generated Dockerfile
	@docker build -t $(BUILT_IMAGE) -f generated_dockerfiles/$(BUILT_IMAGE).dockerfile . --no-cache

##@ Testing

pkg-test: venv ## Run package unit tests with coverage
	@$(VENV_BIN)/pytest tests $(TEST_CASES) -v --cov=src/$(APP) --cov-report=html

pkg-test-with-report: pkg-test ## Run tests and open HTML coverage report
	@$(OPEN) htmlcov/index.html || echo "HTML report not generated, please check the test results in the terminal."

test: pkg-test verify validate ## Run unit tests, verification, and validation

##@ Misc

reuse: ## Annotate files with REUSE license headers
	@find . -name "*.py" -exec reuse annotate --license Apache-2.0 --copyright 'SAP SE or an SAP affiliate company and Gardener contributors' {} +

