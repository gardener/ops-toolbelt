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

import yaml
import os

from lib import commands

def parse_dockerfile_config_yaml(dockerfile_config_path):
    config = None
    with open(dockerfile_config_path, "r") as tools_config_file:
        config = yaml.load(tools_config_file, yaml.SafeLoader)
    if config is None:
        print("Couldnt read from file {}.".format(dockerfile_config_path))
        exit(1)
    return config

def parse_dockerfile_configs(dockerfile_config_paths):
    configs = []
    for dockerfile_config in dockerfile_config_paths:
        for sub_config in dockerfile_config:
            sub_config = parse_dockerfile_config_yaml(os.path.abspath(sub_config))
            configs.extend(sub_config)

    return configs

def parse_commands(configs):
    parsed_commands = []
    command_factory = commands.CommandFactory()
    for config in configs:
        command = command_factory.create(config)
        parsed_commands.append(command)
    return parsed_commands