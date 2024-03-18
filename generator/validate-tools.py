#!/usr/bin/env python3
#
# SPDX-FileCopyrightText: 2024 SAP SE or an SAP affiliate company and Gardener contributors
#
# SPDX-License-Identifier: Apache-2.0

import argparse
import subprocess
import shlex

from lib import dockerfile, commands, config_parser

def validate_tools(commands_list):
    errors = []
    for command in commands_list:
        if isinstance(command, commands.Curl):
            for tool in command.get_tools():
                try:
                    subprocess.run(
                        ["curl", "-sLf", shlex.quote(tool.get_from())],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        check=True)
                except subprocess.CalledProcessError as e:
                    errors.append('Command "{}" failed with exit code {}'.format(e.cmd, e.returncode))
    return errors

parser = argparse.ArgumentParser()
parser.add_argument("--dockerfile-configs", nargs='+', action="append", dest="dockerfile_configs", default=[], required=False, help="yaml file which lists the tools to be tested")
args = parser.parse_args()

dockerfile_config = config_parser.parse_dockerfile_configs(args.dockerfile_configs)
commands_list = config_parser.parse_commands(dockerfile_config)

validation_errors = validate_tools(commands_list)
if len(validation_errors) == 0:
    print("Validation of tools was successful")
    exit(0)
else:
    print("Validation of tools failed with the following errors:\n{}".format('\n'.join(validation_errors)))
    exit(1)