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
from lib import components, utils

class Command:
    required_keys = [
        {"key": "with", "types": str}
    ]

    def __init__(self, config, required_instruction, component_key):
        utils.ConfigValidator.validate_dict(__class__, config)
        self.required_instruction = required_instruction
        self.components = [components.get_component_class(config["with"], component_config) for component_config in config[component_key]]

    def get_lines(self):
        pass

    def get_tools(self):
        return [component for component in self.components]

    def get_tool_names(self):
        return [component.name for component in self.components]

    def get_tool_infos(self):
        return [component.get_info() for component in self.components]

class AptGet(Command):
    required_keys = [
        {"key": "tools", "types": list}
    ]

    def __init__(self, config):
        Command.__init__(self, config, "run", "tools")

    def get_lines(self):
        return (line for line in [
            "apt-get --yes update && apt-get --yes install {}".format(' '.join(self.get_tool_names())),
            "rm -rf /var/lib/apt/lists"
        ])

class Curl(Command):
    required_keys = [
        {"key": "tools", "types": list}
    ]

    def __init__(self, config):
        Command.__init__(self, config, "run", "tools")

    def get_lines(self):
        for tool in self.components:
            if tool.to is not None:
                yield "curl -sLf {} -o {}".format(Curl.get_download_location(tool), tool.to)
            else:
                yield "curl -sLf {} -o /bin/{} && chmod 755 /bin/{}".format(Curl.get_download_location(tool), tool.name, tool.name)

    @staticmethod
    def get_download_location(tool):
        from_url = tool.get_from
        if tool.version is not None:
            from_url = tool.get_from.format(version=tool.version.get())
        return from_url

class Execute(Command):
    required_keys = [
        {"key": "execute", "types": list}
    ]

    def __init__(self, config):
        Command.__init__(self, config, "run", "execute")

    def get_lines(self):
        return (component.command.rstrip() for component in self.components)

class Copy(Command):
    required_keys = [
        {"key": "tools", "types": list}
    ]

    def __init__(self, config,):
        Command.__init__(self, config, "copy", "tools")

    def get_lines(self):
        for component in self.components:
            yield "{} {}".format(component.get_from, component.to)

class Pip(Command):
    required_keys = [
        {"key": "tools", "types": list}
    ]

    def __init__(self, config):
        Command.__init__(self, config, "run", "tools")

    def get_lines(self):
        yield "pip install {}".format(' '.join(self.get_tool_names()))

class Export(Command):
    required_keys = [
        {"key": "export", "types": list}
    ]

    def __init__(self, config):
        Command.__init__(self, config, "env", "export")

    def get_lines(self):
        yield ' '.join(self.get_tool_names())

class AddAptGetRepo(Command):
    required_keys = [
        {"key": "repos", "types": list}
    ]

    def __init__(self, config):
        Command.__init__(self, config, "run", "repos")

    def get_lines(self):
        command = [
            'apt-get --yes update && apt-get --yes install lsb-release gnupg apt-transport-https',
        ]
        for component in self.components:
            repo_name = component.name
            repo_url = component.url
            download_command = [
                'REPO="{}$(lsb_release -cs)"'.format(component.release_prefix),
                'echo "deb {} $REPO main" | tee /etc/apt/sources.list.d/{}.list'.format(repo_url, repo_name),
                'curl -sL {} | apt-key add -'.format(component.key_url),
            ]
            command.extend(download_command)

        command.extend([
            "apt-get --yes --purge remove lsb-release gnupg apt-transport-https",
            "rm -rf /var/lib/apt/lists"
        ])
        return (line for line in command)

class Git(Command):
    required_keys = [
        {"key": "tools", "types": list}
    ]

    def __init__(self, config):
        Command.__init__(self, config, "run", "tools")

    def get_lines(self):
        command_lines = []
        for component in self.components:
            command_lines.append("git -c http.sslVerify=false clone {} {}".format(component.get_from, component.to))
            if component.version is not None:
                command_lines.append('git -C {} checkout {}'.format(component.to, component.version.get()))
        return (line for line in command_lines)


supported_commands = {
    "apt-get": AptGet,
    "curl": Curl,
    "bash": Execute,
    "copy": Copy,
    "pip": Pip,
    "env": Export,
    "add-apt-repo": AddAptGetRepo,
    "git": Git
}

def create_command(config):
    utils.ConfigValidator.validate_dict(Command, config)
    class_name = supported_commands.get(config["with"])
    if class_name is None:
        print("{} is not a supported dockerfile config command".format(config["with"]))
        exit(1)
    instance = class_name(config)
    return instance

def generate_welcome_message(commands):
        basic_tools = []
        custom_shell_commands = []
        exported_environments = []
        for command in commands:
            if isinstance(command, (AptGet, Copy, Curl, Pip, Git)):
                basic_tools.extend([info for info in command.get_tool_infos() if info is not None])
            elif isinstance(command, (Execute)):
                custom_shell_commands.extend([info for info in command.get_tool_infos() if info is not None])
            elif isinstance(command, Export):
                exported_environments.extend([info for info in command.get_tool_infos() if info is not None])
        return """
{}\\n\\
\\n\\
{}\\n\\
The following variables have been exported:\\n\\
{}""".format(' '.join(basic_tools), '\\n\\\n'.join(custom_shell_commands), ' '.join(exported_environments))

