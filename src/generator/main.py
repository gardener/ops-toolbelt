#! /usr/bin/env python3

import yaml

from pathlib import Path
from copy import deepcopy
from pydantic import FilePath, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from generator.models import Dockerfile, InfoGenerator
from generator.utils import directives_to_layers


class ValidateSettings(BaseSettings):
    model_config = SettingsConfigDict(cli_parse_args=True, cli_kebab_case=True)
    dockerfile_config: FilePath


class GeneratorSettings(ValidateSettings):
    from_image: str = "ghcr.io/gardenlinux/gardenlinux:latest"
    title: str = "gardener shell"
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
        # ToDo: we shouldn't deepcopy here
        components=deepcopy(components),
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
