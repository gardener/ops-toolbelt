#! /usr/bin/env python3

# SPDX-FileCopyrightText: 2025 SAP SE or an SAP affiliate company and Gardener contributors
#
# SPDX-License-Identifier: Apache-2.0

import yaml

from pathlib import Path
from copy import deepcopy
from pydantic import FilePath, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from generator.models import BaseItem, Dockerfile, InfoGenerator
from generator.utils import directives_to_layers


class ValidateSettings(BaseSettings):
    model_config = SettingsConfigDict(cli_parse_args=True, cli_kebab_case=True)
    dockerfile_config: FilePath


class GeneratorSettings(ValidateSettings):
    from_image: str = "ghcr.io/gardenlinux/gardenlinux:latest"
    title: str = "gardener shell"
    dockerfile: Path


class ValidationGeneratorSettings(ValidateSettings):
    from_image: str = "ops-toolbelt"
    dockerfile: Path


def validate():
    s = ValidateSettings()  # type: ignore
    with open(s.dockerfile_config, encoding="utf-8") as f:
        try:
            Dockerfile(
                dockerfile_file=Path("/dev/null"),
                components=yaml.safe_load(f),
            )
        except ValidationError as e:
            print(f"Invalid configuration in {s.dockerfile_config}")
            raise e


def generate_dockerfile():
    s = GeneratorSettings()  # type: ignore
    with open(s.dockerfile_config, encoding="utf-8") as f:
        components = yaml.safe_load(f)
    dockerfile = Dockerfile(
        dockerfile_file=s.dockerfile,
        components=components,
        from_image=s.from_image,
        title=s.title,
    )
    info_generator = InfoGenerator(components=components)
    dockerfile.components.append(info_generator)

    with open(dockerfile.dockerfile_file, "w", encoding="utf-8") as cf:
        cf.write(
            dockerfile.to_dockerfile(
                directives_to_layers(dockerfile.components)
            )
        )


def collect_validation_commands(components: list) -> list[tuple[str, str]]:
    """Walk all components and collect (name, validation_command) from items."""
    result = []
    for component in components:
        if not hasattr(component, "items"):
            continue
        for item in component.items:
            if isinstance(item, BaseItem) and item.validation_command:
                result.append((item.name, item.validation_command))
    return result


def generate_validation_dockerfile():
    s = ValidationGeneratorSettings()  # type: ignore
    with open(s.dockerfile_config, encoding="utf-8") as f:
        components = yaml.safe_load(f)
    dockerfile = Dockerfile(
        dockerfile_file=s.dockerfile,
        components=components,
        from_image=s.from_image,
    )

    validation_commands = collect_validation_commands(dockerfile.components)

    lines = [f"FROM {s.from_image}"]
    for name, cmd in validation_commands:
        lines.append(f"# Validate: {name}")
        lines.append(f"RUN {cmd}")

    with open(s.dockerfile, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
