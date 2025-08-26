#!/usr/bin/env python3

"""
Models for the generator package.
"""

import re
import json
from pathlib import Path
from typing import Annotated, Any, Literal
from pydantic_core import core_schema
from functools import partial
from pydantic import (
    BaseModel,
    ConfigDict,
    DirectoryPath,
    Field,
    AfterValidator,
    FilePath,
    HttpUrl,
    field_validator,
    model_validator,
)


def multiline_string_validator(value: str, prefix: str, suffix: str, joiner: str = "\n") -> str:
    """Adds prefixes and suffixes to multiline strings"""
    value = value.strip()
    if '\n' not in value:
        return value
    processed_lines = [f"{prefix}{v}{suffix}" for v in value.splitlines() if v.strip() != ""]
    processed_lines[-1] = processed_lines[-1].removesuffix(suffix)
    processed_lines[0] = processed_lines[0].removeprefix(prefix)
    return joiner.join(processed_lines)


def package_name_string_validator(value: str) -> str:
    if value.strip() and not re.match(r"^[a-zA-Z0-9_/\s-]+$", value):
        raise ValueError(
            f"Invalid package name: '{value}'. Only alphanumeric characters, underscores and hyphens are allowed."
        )
    return value


def ensure_env_pair(value: str) -> str:
    if "=" not in value:
        raise ValueError(
            f"Invalid environment variable format: '{value}'. Expected 'KEY=VALUE'."
        )
    k, v = value.split("=", 1)
    if len(k) == 0 or len(v) == 0:
        raise ValueError(
            f"Invalid environment variable format: '{value}'. Both key and value must be non-empty."
        )
    return value


command_multiline_string_validator = partial(multiline_string_validator, prefix="    ", suffix=";\\")
info_multiline_string_validator = partial(multiline_string_validator, prefix="", suffix="", joiner="\\n")

SupportedDockerfileCommands = Literal["ARG", "RUN", "ENV", "COPY"]
PackageNameString = Annotated[str, AfterValidator(package_name_string_validator)]
CommandString = Annotated[str, AfterValidator(command_multiline_string_validator)]
InfoString = Annotated[str, AfterValidator(info_multiline_string_validator)] | None

class OpinionatedBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class BaseItem(OpinionatedBaseModel):
    name: PackageNameString
    info: InfoString = None

    def dump_ghelp(self) -> tuple[PackageNameString, str | None, InfoString]:
        return self.name, getattr(self, 'version', None), self.info


class BaseDockerfileDirective(OpinionatedBaseModel):
    key: SupportedDockerfileCommands
    can_be_combined: bool = True

    def to_shortened_dockerfile_directive(self) -> str:
        """Only the command part of the dockerfile directive"""
        raise NotImplementedError("Subclasses must implement this method.")

    def to_dockerfile_directive(self) -> str:
        """Full dockerfile directive"""
        return f"{self.key} {self.to_shortened_dockerfile_directive()}"

    def to_ghelp_format(self) -> list:
        """Convert items to ghelp format"""
        if not hasattr(self, "items"):
            raise NotImplementedError(f"{self.__class__.__name__} must have 'items' attribute.")
        return [item.dump_ghelp() for item in self.items]  # type: ignore


class BashItem(BaseItem):
    command: CommandString

class BashItemList(BaseDockerfileDirective):
    name: Literal["bash"]
    items: list[BashItem]
    key: SupportedDockerfileCommands = "RUN"

    @field_validator("items", mode="before")
    @classmethod
    def convert_string_to_bash_item(cls, value: list[Any]) -> list[BashItem]:
        result = []
        for item in value:
            if isinstance(item, str):
                item = BashItem(name="bash", command=item)
            result.append(item)
        return result

    def to_shortened_dockerfile_directive(self) -> str:
        return ";\\\n    ".join(bash.command for bash in self.items)


class AptGetItem(BaseItem):
    provides: PackageNameString | list[PackageNameString]

    @model_validator(mode="before")
    @classmethod
    def fill_provides_if_empty(cls, data: Any) -> Any:
        if isinstance(data, str):
            return data
        if isinstance(data, dict):
            if "provides" not in data:
                data["provides"] = data["name"]
            return data
        raise ValueError(f"Input not as expected {data}")

    def dump_ghelp(self) -> tuple[PackageNameString, PackageNameString | list[PackageNameString]]:
        return self.name, self.provides


class AptGetItemList(BaseDockerfileDirective):
    name: Literal["apt-get"]
    items: list[AptGetItem | PackageNameString]
    key: SupportedDockerfileCommands = "RUN"
    apt_get_command: str = Field(
        default="apt-get --yes update && apt-get --yes install",
        alias="apt-get-command",
    )

    def to_shortened_dockerfile_directive(self) -> str:
        return (
            f"{self.apt_get_command} "
            + " ".join(
                item.name if isinstance(item, AptGetItem) else item
                for item in self.items
            )
            + """;\\
    rm -rf /var/lib/apt/lists"""
        )

    def to_ghelp_format(self) -> list:
        """Convert items to ghelp format"""
        return [
            item.dump_ghelp() if isinstance(item, AptGetItem) else (item, item)
            for item in self.items
        ]


class ShellAwareHttpUrl(str):
    def __new__(cls, v: str) -> "ShellAwareHttpUrl":
        """Create new instance after validation"""
        validated = cls.validate(v)
        return super().__new__(cls, validated)

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):

        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.str_schema(),
        )

    @classmethod
    def validate(cls, v: str) -> str:
        """
        Validate a URL that may contain shell variables or command substitutions.
        Replace shell constructs with placeholder values for URL validation.
        """
        var_pattern = r"(?<!\\)\$(?:[a-zA-Z_][a-zA-Z0-9_]*|\{[^}]+\})"
        subshell_pattern = r"(?<!\\)(?:\$\([^)]+\)|`[^`]+`)"

        _val = v

        _val = re.sub(var_pattern, "placeholder", _val)
        _val = re.sub(subshell_pattern, "placeholder", _val)

        try:
            HttpUrl(_val)
        except Exception as e:
            raise ValueError(f"Invalid URL: {v}") from e

        return v

class OptionalFormatedDict(dict):
    """ Dict that will return missing dict keys as {key}"""

    def __missing__(self, key: str) -> Any:
        return "{" + key + "}"

class CurlItem(BashItem):
    version: str = ""
    source: ShellAwareHttpUrl = Field(alias="from")
    to: Path
    command: CommandString = ""

    @model_validator(mode="before")
    @classmethod
    def template_url(cls, data: Any) -> Any:
        if isinstance(data["from"], str):
            data["from"] = data["from"].format_map(OptionalFormatedDict(version=data.get("version", "")))
        return data

    @model_validator(mode="before")
    @classmethod
    def fill_to_if_empty(cls, data: Any) -> Any:
        if isinstance(data, dict):
            data["to"] = data.get("to", f"/bin/{data['name']}")
        return data

    @model_validator(mode="after")
    @classmethod
    def fill_command(cls, data: Any) -> Any:
        cmd = f"curl -sLf {data.source} -o {data.to}"
        if not data.command:
            data.command = f"chmod 755 {data.to}"
        data.command = f"{cmd} && {data.command}"
        return data

    def dump_ghelp(self) -> tuple[str, str | None, str | None]:
        """Dump ghelp format for curl item"""
        return self.name, self.version or None, self.info or None


class CurlItemList(BaseDockerfileDirective):
    name: Literal["curl"]
    items: list[CurlItem]
    key: SupportedDockerfileCommands = "RUN"

    def to_shortened_dockerfile_directive(self) -> str:
        return ";\\\n    ".join([c.command for c in self.items])

    def to_ghelp_format(self) -> list:
        return [i.dump_ghelp() for i in self.items]


EnvString = Annotated[str, AfterValidator(ensure_env_pair)]


class EnvItemList(BaseDockerfileDirective):
    name: Literal["env"]
    items: list[EnvString]
    key: SupportedDockerfileCommands = "ENV"

    def to_shortened_dockerfile_directive(self):
        return " ".join(self.items)


class CopyItem(BaseItem):
    source: FilePath | DirectoryPath = Field(alias="from")
    to: Path
    command: str = Field(default="", description="Arguments for COPY directive")
    key: SupportedDockerfileCommands = "COPY"

    @field_validator("command", mode="after")
    @classmethod
    def prepend_empty_space_to_command(cls, value: str) -> str:
        if value:
            if value[0] != " ":
                return f" {value}"
        return value

    def to_dockerfile_directive(self) -> str:
        return f"{self.key}{self.command} {self.source} {self.to}"


class CopyItemList(BaseDockerfileDirective):
    name: Literal["copy"]
    items: list[CopyItem]
    key: SupportedDockerfileCommands = "COPY"
    can_be_combined: bool = False

    def to_shortened_dockerfile_directive(self) -> str:
        return "\n".join([c.to_dockerfile_directive() for c in self.items])

    def to_dockerfile_directive(self) -> str:
        return self.to_shortened_dockerfile_directive()


class ArgItemList(BaseDockerfileDirective):
    name: Literal["arg"]
    items: list[str]
    key: SupportedDockerfileCommands = "ARG"
    can_be_combined: bool = False

    def to_shortened_dockerfile_directive(self) -> str:
        return "\n".join([f"ARG {item}" for item in self.items])

    def to_dockerfile_directive(self) -> str:
        return self.to_shortened_dockerfile_directive()


class DockerfileLayer(OpinionatedBaseModel):
    key: SupportedDockerfileCommands
    commands: list[str]

    def __str__(self) -> str:
        return ";\\\n".join(self.commands)


class InfoGenerator(OpinionatedBaseModel):
    key: SupportedDockerfileCommands = "RUN"
    name: Literal["you-shall not use this"] = "you-shall not use this"
    components: list[
        Annotated[
            AptGetItemList
            | CopyItemList
            | CurlItemList
            | BashItemList
            | EnvItemList
            | ArgItemList,
            Field(discriminator="name"),
        ]
    ]
    can_be_combined: bool = True

    def to_ghelp_format(self) -> dict:
        """Convert components to ghelp.json format"""
        result = {"apt": [], "pip": [], "downloaded": []}

        for component in self.components:
            if isinstance(component, AptGetItemList):
                result["apt"].extend(component.to_ghelp_format())
                continue
            if isinstance(component, CurlItemList):
                result["downloaded"].extend(component.to_ghelp_format())
                continue
            if isinstance(component, (BashItemList, CopyItemList)):
                result["downloaded"].extend(component.to_ghelp_format())
                continue

        return result

    def to_shortened_dockerfile_directive(self) -> str:
        return f"echo '{json.dumps(self.to_ghelp_format())}' > /var/lib/ghelp_info"


class Dockerfile(OpinionatedBaseModel):
    dockerfile_file: Path
    title: str = "gardener shell"
    from_image: str = "ghcr.io/gardenlinux/gardenlinux:latest"
    components: list[
        Annotated[
            AptGetItemList
            | CopyItemList
            | CurlItemList
            | BashItemList
            | EnvItemList
            | ArgItemList
            | InfoGenerator,
            Field(discriminator="name"),
        ]
    ]

    def to_dockerfile(self, layers: list[DockerfileLayer]) -> str:
        return f"FROM {self.from_image}\n{'\n'.join([str(l) for l in layers])}"
