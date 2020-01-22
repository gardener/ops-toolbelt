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
from lib import validation

class BaseComponentConfig:
    def __init__(self, name, info):
        self.name = name
        self.info = info

    def get_info(self):
        return self.info

    def get_name(self):
        return self.name

    def get_provided_apps(self):
        return self.name

class StringComponentConfig(BaseComponentConfig):
    def __init__(self, config):
        validation.ConfigValidator.validate_str(__class__, config)
        super().__init__(config, config)

class DictComponentConfig(BaseComponentConfig):
    required_keys = [
        {"key": "name", "types":(str)},
    ]
    optional_keys = [
        {"key": "info", "types":(str, type(None))},
        {"key": "provides", "types":(str, list, type(None))}
    ]

    def __init__(self, config):
        validation.ConfigValidator.validate_dict(__class__, config)
        name = config["name"]
        if "info" in config.keys():
            info = config.get("info")
        else:
            info = name
        super().__init__(name, info)
        self.provides = config.get("provides")

    def get_provided_apps(self):
        return self.provides

class ToolConfig(DictComponentConfig):
    required_keys = [
        {"key": "from", "types": (str)}
    ]
    optional_keys = [
        {"key": "to", "types": (str)},
        {"key": "command", "types": (dict)},
        {"key": "version", "types": (str)},
    ]

    def __init__(self, config):
        DictComponentConfig.__init__(self, config)
        self._from = config["from"]
        self.to = config.get("to")
        self.command = config.get("command")
        self.version = config.get("version")

    def get_to(self):
        if self.to is None:
            return None
        if self.version is not None:
            return self.to.format(version=self.get_version())
        return self.to

    def get_from(self):
        _from = self._from
        if self.version is not None:
            _from = _from.format(version=self.get_version())
        return _from

    def get_command(self):
        return self.command

    def get_version(self):
        return self.version

class BashCommandConfig(DictComponentConfig):
    required_keys = [
        {"key": "command", "types": (str)}
    ]
    def __init__(self, config):
        DictComponentConfig.__init__(self, config)
        self.command = config["command"]

    def get_command(self):
        return self.command

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

    def get_release_prefix(self):
        return self.release_prefix

    def get_repo_url(self):
        return self.url

    def get_key_url(self):
        return self.key_url


class ComponentConfigParser:
    registered_classes = [StringComponentConfig, DictComponentConfig, BashCommandConfig, ToolConfig, AptRepoConfig]

    def __init__(self, *argv):
        for component_class in argv:
            if component_class not in ComponentConfigParser.registered_classes:
                raise TypeError("Unsupported class for components: {}.".format(component_class))
        self.component_classes = argv

    def parse_components(self, component_configs):
        components = []
        for config in component_configs:
            lastErr = None
            component = None
            for clazz in self.component_classes:
                try:
                    component = clazz(config)
                except TypeError as err:
                    lastErr = err
                    continue
            if component is None and lastErr is not None:
                raise lastErr
            components.append(component)
        return components

