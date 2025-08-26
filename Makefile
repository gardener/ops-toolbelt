SHELL := /usr/bin/env bash
PYTHON := python3
VENV_DIR = .venv
VENV_BIN = $(VENV_DIR)/bin
VENV_PIP = $(VENV_BIN)/pip
APP = generator
IMAGE_TAG ?= $(shell yq '.componentReferences[] | select(.name == "gardenlinux") | .version' .ocm/base-component.yaml)
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


help:
	@echo "Usage:"
	@echo "  Scripting related:"
	@echo "    make venv                      - Create or update the virtual environment"
	@echo "    make ensure-venv               - Ensure the virtual environment exists"
	@echo "    make verify-bandit             - Run bandit security checks"
	@echo "    make verify-shellcheck         - Run shellcheck on scripts"
	@echo "    make verify                    - Run verification checks (linting and static code checks)"
	@echo "    make pkg-test                  - Run package unit tests"
	@echo "    make pkg-test-with-report      - Run package unit tests, open coverage report in browser"
	@echo "    make test                      - Run all tests"
	@echo "  Package related:"
	@echo "    make build                     - Generate Dockerfile. Builds upon gardenlinux latest tag, set the IMAGE_REPO and IMAGE_TAG envs"
	@echo "    make validate                  - Validate the generator configuration"
	@echo "    make build-image               - Build the Docker image from the generated Dockerfile"

ensure-venv:
	@if [ ! -d ".venv" ]; then $(MAKE) venv-build; fi

ensure-shellcheck:
	@command -v shellcheck > /dev/null || { echo "shellcheck is not installed. Please install shellcheck"; exit 1; }
	@if ! command -v shellcheck-sarif > /dev/null; then cargo install shellcheck-sarif; fi

venv-build:
	@$(PYTHON) -m venv .venv
	@$(MAKE) venv-update
	@echo "Virtual environment created. Run $(red)'source .venv/bin/activate'$(color_reset) to activate it."

venv-update: ensure-venv
	@$(VENV_PIP) install --upgrade pip; $(VENV_PIP) install -e '.[dev]'

venv: venv-update

verify-bandit: ensure-venv
	@VENV_BIN=$(VENV_BIN) .ci/verify-bandit

verify-shellcheck: ensure-shellcheck
	@.ci/verify-shellcheck

verify: verify-bandit verify-shellcheck

validate: venv
	$(VENV_BIN)/generator-validate --dockerfile-config dockerfile-configs/common-components.yaml

build: ensure-venv
	@echo Generating dockerfile
	@$(VENV_BIN)/generator \
		--from-image $(IMAGE_REPO):$(IMAGE_TAG) \
		--dockerfile-config dockerfile-configs/common-components.yaml \
		--dockerfile generated_dockerfiles/$(BUILT_IMAGE).dockerfile

build-image: build
	@docker build -t $(BUILT_IMAGE) -f generated_dockerfiles/$(BUILT_IMAGE).dockerfile . --no-cache

pkg-test: venv
	@$(VENV_BIN)/pytest tests $(TEST_CASES) -v --cov=src/$(APP) --cov-report=html

pkg-test-with-report: pkg-test
	@$(OPEN) htmlcov/index.html || echo "HTML report not generated, please check the test results in the terminal."

test: pkg-test verify validate

reuse:
	@find . -name "*.py" -exec reuse annotate --license Apache-2.0 --copyright 'SAP SE or an SAP affiliate company and Gardener contributors' {} +
