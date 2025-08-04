# s.from_imagss /usr/bin/env python3

"""
Models for the generator package.
"""

import re
from pathlib import Path
from typing import Annotated, Any, Literal
from pydantic import (
    BaseModel,
    DirectoryPath,
    Field,
    AfterValidator,
    FilePath,
    HttpUrl,
    field_validator,
    model_validator,
)


def package_name_string_validator(value: str) -> str:
    if re.search(r"[\s,.\\]", value):
        raise ValueError(
            f"Invalid package name: '{value}'. Only alphanumeric characters, underscores and hyphens are allowed."
        )
    return value


def ensure_env_key_pair(value: str) -> str:
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


SupportedfileCommands = Literal["ARG", "RUN", "ENV", "COPY"]
PackageNameString = Annotated[str, Field(AfterValidator(package_name_string_validator))]
CommandString = str


class BaseItem(BaseModel):
    name: PackageNameString
    info: str | None = None


class BaseContainerfileDirective(BaseModel):
    key: SupportedfileCommands

    def to_shortened_containerfile_directive(self) -> str:
        """Only the command part of the containerfile directive"""
        raise NotImplementedError("Subclasses must implement this method.")

    def to_containerfile_directive(self) -> str:
        """Full containerfile directive"""
        return f"{self.key} {self.to_shortened_containerfile_directive()}"


class BashItem(BaseItem):
    command: CommandString


class BashItemList(BaseContainerfileDirective):
    name: Literal["bash"]
    items: list[BashItem]
    key: SupportedfileCommands = "RUN"

    def to_shortened_containerfile_directive(self) -> str:
        return ";\\\n    ".join(bash.command for bash in self.items)

    def to_containerfile_directive(self) -> str:
        return f"{self.key} {self.to_shortened_containerfile_directive()}"


class AptGetItem(BaseItem):
    provides: PackageNameString | list[PackageNameString]

    @model_validator(mode="before")
    @classmethod
    def fill_providers_if_empty(cls, data: Any) -> Any:
        if isinstance(data, str):
            return data
        if isinstance(data, dict):
            if "provides" not in data:
                data["provides"] = data["name"]
        return data


class AptGetItemList(BaseContainerfileDirective):
    name: Literal["apt-get"]
    items: list[AptGetItem | PackageNameString]
    key: SupportedfileCommands = "RUN"
    apt_get_command: str = Field(
        default="apt-get update -y && apt-get install -y",
        alias="apt-get-command",
    )

    def to_shortened_containerfile_directive(self) -> str:
        return f"{self.apt_get_command} " + " ".join(
            item.name if isinstance(item, AptGetItem) else item for item in self.items
        )

    def to_containerfile_directive(self) -> str:
        return f"{self.key} {self.to_shortened_containerfile_directive()}"


class CurlItem(BaseItem):
    version: str = ""
    source: HttpUrl = Field(alias="from")
    to: Path
    command: CommandString = ""

    @model_validator(mode="before")
    @classmethod
    def template_url(cls, data: Any) -> Any:
        if isinstance(data["from"], str):
            data["from"] = data["from"].format(version=data.get("version", ""))
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


class CurlItemList(BaseContainerfileDirective):
    name: Literal["curl"]
    items: list[CurlItem]
    key: SupportedfileCommands = "RUN"

    def to_shortened_containerfile_directive(self) -> str:
        return ";\\\n    ".join([c.command for c in self.items])

    def to_containerfile_directive(self) -> str:
        return f"{self.key} {self.to_shortened_containerfile_directive()}"


EnvString = Annotated[str, Field(AfterValidator(ensure_env_key_pair))]


class EnvItemList(BaseContainerfileDirective):
    name: Literal["env"]
    items: list[EnvString]
    key: SupportedfileCommands = "ENV"

    def to_shortened_containerfile_directive(self):
        return " ".join(self.items)


class CopyItem(BaseItem):
    source: FilePath | DirectoryPath = Field(alias="from")
    to: Path
    command: str = Field(default="", description="Arguments for COPY directive")
    key: SupportedfileCommands = "COPY"

    @field_validator("command", mode="after")
    @classmethod
    def prepend_empty_space_to_command(cls, value: str) -> str:
        if value:
            if value[0] != " ":
                return f" {value}"
        return value

    def to_containerfile_directive(self) -> str:
        return f"{self.key}{self.command} {self.source} {self.to}"


class CopyItemList(BaseContainerfileDirective):
    name: Literal["copy"]
    items: list[CopyItem]
    key: SupportedfileCommands = "COPY"

    def to_shortened_containerfile_directive(self) -> str:
        return "\n".join([c.to_containerfile_directive() for c in self.items])

    def to_containerfile_directive(self) -> str:
        return self.to_shortened_containerfile_directive()


class Containerfile(BaseModel):
    container_file: Path
    title: str = "gardener shell"
    from_image: str = "ghcr.io/gardenlinux/gardenlinux:latest"
    components: list[
        Annotated[
            AptGetItemList | CopyItemList | CurlItemList | BashItemList | EnvItemList,
            Field(discriminator="name"),
        ]
    ]
