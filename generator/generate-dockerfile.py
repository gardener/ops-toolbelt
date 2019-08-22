#!/usr/bin/python
#
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

import sys


def main(argv):
    pass


if __name__ == '__main__':
    main(sys.argv)
#!/usr/bin/env python3

import argparse
import os

from lib import dockerfile, commands, utils

parser = argparse.ArgumentParser()
parser.add_argument("--dockerfile-config", dest="dockerfile_config", required=True, help="yaml file which lists the tools to be added to the toolbelt dockerfile.")
parser.add_argument("--additional-configs", nargs='+', action="append", dest="additional_configs", default=[], required=False, help="Additional tools to add to the toolbelt dockerfile.")
parser.add_argument("--from-image", dest="from_image", required=True, default=None, help="Base image to use for the dockerfile.")
parser.add_argument("--add-welcome-message", dest="add_welcome_message", required=False, default=True, help="Whether to generate a welcome message containing the installed tools")
parser.add_argument("--dockerfile", dest="dockerfile", required=True, help="File in which to save the generated dockerfile")
args = parser.parse_args()

dockerfile_config = utils.parse_dockerfile_configs(args.dockerfile_config, args.additional_configs)
commands_list = [commands.create_command(command_config) for command_config in dockerfile_config]

dockerfile = dockerfile.Dockerfile(args.from_image, commands_list)
dockerfile.create()

if args.add_welcome_message:
    motd = commands.generate_welcome_message(commands_list)
    dockerfile.add_welcome_message(motd)

with open(os.path.abspath(args.dockerfile), "w") as f:
    f.write(dockerfile.to_string())