#! /usr/bin/env python3

# SPDX-FileCopyrightText: 2025 SAP SE or an SAP affiliate company and Gardener contributors
#
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

import pytest

from generator.main import collect_validation_commands
from generator.models import (
    AptGetItemList,
    BashItemList,
    CopyItemList,
    CurlItemList,
    Dockerfile,
    EnvItemList,
)


def make_dockerfile(components: list) -> Dockerfile:
    return Dockerfile(
        dockerfile_file=Path("/dev/null"),
        components=components,
    )


def test_collect_validation_commands_from_curl_items():
    components = [
        CurlItemList.model_validate({
            "name": "curl",
            "items": [
                {
                    "name": "kubectl",
                    "from": "http://example.com/kubectl",
                    "validation_command": "kubectl version --client",
                },
                {
                    "name": "nerdctl",
                    "from": "http://example.com/nerdctl",
                },
            ],
        })
    ]
    df = make_dockerfile(components)
    result = collect_validation_commands(df.components)
    assert result == [("kubectl", "kubectl version --client")]


def test_collect_validation_commands_from_bash_items():
    components = [
        BashItemList.model_validate({
            "name": "bash",
            "items": [
                {
                    "name": "locale",
                    "command": "locale-gen",
                    "validation_command": "locale -a | grep en_US",
                },
                {
                    "name": "other",
                    "command": "echo hi",
                },
            ],
        })
    ]
    df = make_dockerfile(components)
    result = collect_validation_commands(df.components)
    assert result == [("locale", "locale -a | grep en_US")]


def test_collect_validation_commands_from_apt_get_items():
    components = [
        AptGetItemList.model_validate({
            "name": "apt-get",
            "items": [
                {"name": "jq", "validation_command": "jq --version"},
                "curl",  # plain string, no validation_command
                {"name": "vim-tiny"},
            ],
        })
    ]
    df = make_dockerfile(components)
    result = collect_validation_commands(df.components)
    assert result == [("jq", "jq --version")]


def test_collect_validation_commands_skips_env_and_arg():
    components = [
        EnvItemList.model_validate({
            "name": "env",
            "items": ["KEY=val"],
        })
    ]
    df = make_dockerfile(components)
    result = collect_validation_commands(df.components)
    assert result == []


def test_collect_validation_commands_empty():
    df = make_dockerfile([])
    result = collect_validation_commands(df.components)
    assert result == []


def test_collect_validation_commands_mixed(mocker):
    mocker.patch("pathlib.Path.is_file", return_value=True)
    mocker.patch("pathlib.Path.is_dir", return_value=True)
    mocker.patch("pathlib.Path.exists", return_value=True)

    components = [
        AptGetItemList.model_validate({
            "name": "apt-get",
            "items": [
                {"name": "jq", "validation_command": "jq --version"},
                "curl",
            ],
        }),
        CurlItemList.model_validate({
            "name": "curl",
            "items": [
                {
                    "name": "kubectl",
                    "from": "http://example.com/kubectl",
                    "validation_command": "kubectl version --client",
                },
            ],
        }),
        BashItemList.model_validate({
            "name": "bash",
            "items": [{"name": "setup", "command": "echo hi"}],
        }),
        CopyItemList.model_validate({
            "name": "copy",
            "items": [
                {
                    "name": "scripts",
                    "from": "/src",
                    "to": "/dst",
                    "validation_command": "test -d /dst",
                },
            ],
        }),
    ]
    df = make_dockerfile(components)
    result = collect_validation_commands(df.components)
    assert result == [
        ("jq", "jq --version"),
        ("kubectl", "kubectl version --client"),
        ("scripts", "test -d /dst"),
    ]


def test_generate_validation_dockerfile(tmp_path, mocker):
    config_content = """
- name: curl
  items:
  - name: kubectl
    from: http://example.com/kubectl
    validation_command: kubectl version --client
  - name: tool
    from: http://example.com/tool
- name: bash
  items:
  - name: setup
    command: echo hi
    validation_command: echo ok
"""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(config_content)
    output_file = tmp_path / "Dockerfile.validation"

    mocker.patch(
        "generator.main.ValidationGeneratorSettings",
        return_value=mocker.Mock(
            dockerfile_config=config_file,
            from_image="my-image:latest",
            dockerfile=output_file,
        ),
    )

    from generator.main import generate_validation_dockerfile

    generate_validation_dockerfile()

    content = output_file.read_text()
    assert content == (
        "FROM my-image:latest\n"
        "# Validate: kubectl\n"
        "RUN kubectl version --client\n"
        "# Validate: setup\n"
        "RUN echo ok\n"
    )
