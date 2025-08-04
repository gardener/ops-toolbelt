#! /usr/bin/env python3

import yaml

from pathlib import Path
from pydantic import FilePath, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from generator.models import Containerfile


class ValidateSettings(BaseSettings):
    model_config = SettingsConfigDict(cli_parse_args=True, cli_kebab_case=True)
    dockerfile_config: FilePath


class GeneratorSettings(ValidateSettings):
    from_image: str
    title: str
    dockerfile: Path


def validate():
    s = ValidateSettings()
    with open(s.dockerfile_config, encoding="utf-8") as f:
        Containerfile(
            container_file=Path("/dev/null"),
            components=yaml.safe_load(f),
        )
