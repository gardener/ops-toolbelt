#!/usr/bin/env python3
#
# SPDX-FileCopyrightText: 2024 SAP SE or an SAP affiliate company and Gardener contributors
#
# SPDX-License-Identifier: Apache-2.0

import argparse
import subprocess  # nosec B404  # We don't have the exploitable B602 and can't go without subprocess
import shlex
import re

from lib import commands, config_parser

def validate_tools(commands_list):
    errors = []
    for command in commands_list:
        if isinstance(command, commands.Curl):
            for tool in command.get_tools():
                cmd_line = tool.get_from()
                cmd_line = re.sub(r"\$\(echo \${TARGETARCH}.*\)", "amd64", cmd_line)
                cmd_line = re.sub(r"\${TARGETARCH}", "amd64", cmd_line)
                try:
                    # Shell is set to false to limit the change for shell injection
                    # but we need check=true to get the return code
                    # as this is the actual validation of commands.
                    # B603 is disabled for that reason
                    subprocess.run(
                        ["/usr/bin/curl", "-sLf", shlex.quote(cmd_line)],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        check=True,
                        shell=False
                    )  # nosec B603
                except subprocess.CalledProcessError as e:
                    errors.append(f'Command "{e.cmd}" failed with exit code {e.returncode}')
    return errors


parser = argparse.ArgumentParser()
parser.add_argument("--dockerfile-configs", nargs='+', action="append", dest="dockerfile_configs",
                    default=[], required=False, help="yaml file which lists the tools to be tested")
args = parser.parse_args()

dockerfile_config = config_parser.parse_dockerfile_configs(args.dockerfile_configs)
commands_list = config_parser.parse_commands(dockerfile_config)

validation_errors = validate_tools(commands_list)
if len(validation_errors) == 0:
    print("Validation of tools was successful")
    exit(0)

validation_errors_str: str = "\n".join(validation_errors)
print(f"Validation of tools failed with the following errors:\n{validation_errors_str}")
exit(1)
