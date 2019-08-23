# Copyright 2019 Copyright (c) 2019 SAP SE or an SAP affiliate company. All rights reserved. This file is licensed under the Apache Software License, v. 2 except as noted otherwise in the LICENSE file.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import subprocess
import shlex
from lib import utils

class VersionConfig:
    def __init__(self, config):
        pass
    def get(self):
        pass

    @staticmethod
    def parse_version_config(config):
        if isinstance(config, str):
            return StringVersionConfig(config)
        elif isinstance(config, dict):
            return VersionFromUrl(config)
        elif config is None or isinstance(config, type(None)):
            return None

class StringVersionConfig(VersionConfig):
    def __init__(self, version):
        utils.ConfigValidator.validate_str(__class__, version)
        self.version = version

    def get(self):
        return self.version

class VersionFromUrl(VersionConfig):
    required_keys = [
        {"key": "from-url", "types": str}
    ]
    def __init__(self, config):
        utils.ConfigValidator.validate_dict(__class__, config)
        self.url = config["from-url"]

    def get(self):
        try:
            output = subprocess.run(["curl", "-sLf", shlex.quote(self.url)], text=True, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            return "Error retrieving version: {}".format(e.stderr)
        return output.stdout.strip()

class BaseComponentConfig:
    def __init__(self, name, info):
        self.name = name
        self.info = info

    def get_info(self):
        return self.info

class StringComponentConfig(BaseComponentConfig):
    def __init__(self, config):
        utils.ConfigValidator.validate_str(__class__, config)
        super().__init__(config, config)

class DictComponentConfig(BaseComponentConfig):
    required_keys = [
        {"key": "name", "types":(str)},
    ]
    optional_keys = [
        {"key": "version", "types": (str, dict)},
        {"key": "info", "types":(str, type(None))}
    ]

    def __init__(self, config):
        utils.ConfigValidator.validate_dict(__class__, config)
        name = config["name"]
        if "info" in config.keys():
            info = config.get("info")
        else:
            info = name
        super().__init__(name, info)
        self.version = VersionConfig.parse_version_config(config.get("version"))


class ToolConfig(DictComponentConfig):
    required_keys = [
        {"key": "from", "types": (str)}
    ]
    optional_keys = [
        {"key": "to", "types": (str)},
    ]

    def __init__(self, config):
        DictComponentConfig.__init__(self, config)
        self.get_from = config["from"]
        self.to = config.get("to")

class BashCommandConfig(DictComponentConfig):
    required_keys = [
        {"key": "command", "types": (str)}
    ]
    def __init__(self, config):
        DictComponentConfig.__init__(self, config)
        self.command = config["command"]

class AptRepoConfig(DictComponentConfig):
    required_keys = [
        {"key": "url", "types": (str)},
        {"key": "key-url", "types": (str)}
    ]

    optional_keys = [
        {"key": "release-prefix", "types": (str)}
    ]
    def __init__(self, config):
        DictComponentConfig.__init__(self, config)
        self.release_prefix = config.get("release-prefix", "")
        self.url = config["url"]
        self.key_url = config["key-url"]

tools_for_commands = {
    "apt-get": StringComponentConfig,
    "curl": ToolConfig,
    "bash": BashCommandConfig,
    "copy": ToolConfig,
    "pip": StringComponentConfig,
    "env": StringComponentConfig,
    "add-apt-repo": AptRepoConfig,
    "git": ToolConfig
}

def get_component_class(command, config):
    class_name = tools_for_commands.get(command)
    if class_name is None:
        print("No supported component configs for command {}.".format(command))
        exit(1)
    obj = class_name(config)
    return obj
