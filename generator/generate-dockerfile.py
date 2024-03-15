#!/usr/bin/env python3
#
# SPDX-FileCopyrightText: 2024 SAP SE or an SAP affiliate company and Gardener contributors
#
# SPDX-License-Identifier: Apache-2.0

import argparse
import os

from lib import commands, config_parser, dockerfile

parser = argparse.ArgumentParser()
parser.add_argument("--dockerfile-configs", nargs='+', action="append", dest="dockerfile_configs", default=[], required=False, help="yaml files which lists the tools to be added to the toolbelt dockerfile.")
parser.add_argument("--from-image", dest="from_image", required=True, default=None, help="Base image to use for the dockerfile.")
parser.add_argument("--title", dest="title", required=True, help="Welcome message title")
parser.add_argument("--dockerfile", dest="dockerfile", required=True, help="File in which to save the generated dockerfile")
args = parser.parse_args()

dockerfile_config = config_parser.parse_dockerfile_configs(args.dockerfile_configs)
commands_list = config_parser.parse_commands(dockerfile_config)

info_generator = commands.InfoGenerator(commands_list)
ghelp_info = info_generator.generate_help_command_info()

dockerfile = dockerfile.Dockerfile(args.from_image, commands_list)
dockerfile.create()

dockerfile.add_welcome_message(args.title)
dockerfile.add_ghelp_info(ghelp_info)

with open(os.path.abspath(args.dockerfile), "w") as f:
    f.write(dockerfile.to_string())