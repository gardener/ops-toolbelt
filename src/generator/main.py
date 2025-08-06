#! /usr/bin/env python3

import yaml

from pathlib import Path
from pydantic import FilePath, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from generator.models import Containerfile
from generator.utils import directives_to_layers


class ValidateSettings(BaseSettings):
    model_config = SettingsConfigDict(cli_parse_args=True, cli_kebab_case=True)
    dockerfile_config: FilePath


class GeneratorSettings(ValidateSettings):
    from_image: str = "ghcr.io/gardenlinux/gardenlinux:latest"
    title: str = "gardener shell"
    dockerfile: Path


def validate():
    s = ValidateSettings()
    with open(s.dockerfile_config, encoding="utf-8") as f:
        Containerfile(
            container_file=Path("/dev/null"),
            components=yaml.safe_load(f),
        )


def generate_containerfile():
    s = GeneratorSettings()
    with open(s.dockerfile_config, encoding="utf-8") as f:
        containerfile = Containerfile(
            container_file=s.dockerfile,
            components=yaml.safe_load(f),
            from_image=s.from_image,
            title=s.title,
        )
    with open("/tmp/containerfile", "w", encoding="utf-8") as cf:
        # with open(containerfile.container_file, "w", encoding="utf-8") as cf:
        cf.write(
            containerfile.to_containerfile(
                directives_to_layers(containerfile.components)
            )
        )
