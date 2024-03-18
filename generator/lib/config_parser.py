# SPDX-FileCopyrightText: 2024 SAP SE or an SAP affiliate company and Gardener contributors
#
# SPDX-License-Identifier: Apache-2.0

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