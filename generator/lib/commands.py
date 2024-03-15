# SPDX-FileCopyrightText: 2024 SAP SE or an SAP affiliate company and Gardener contributors
#
# SPDX-License-Identifier: Apache-2.0

import json
from lib import components, dockerfile

class Command:
    def __init__(self, components, dockerfile_instruction):
        self.components = components
        self.dockerfile_instruction = dockerfile_instruction

    def get_lines(self):
        pass

    def get_tools(self):
        return [component for component in self.components]

    def get_tool_names(self):
        return [component.get_name() for component in self.components]

    def get_tool_infos(self):
        return [component.get_info() for component in self.components]

    def join(self, other):
        return self.components.extend(other.components)

    def version_check(self):
        pass

class AptGet(Command):
    def __init__(self, components):
        Command.__init__(self, components, dockerfile.RUN)

    def get_lines(self):
        return (line for line in [
            "apt-get --yes update && apt-get --yes install {}".format(' '.join(self.get_tool_names())),
            "rm -rf /var/lib/apt/lists"
        ])

class Curl(Command):
    def __init__(self, components):
        Command.__init__(self, components, dockerfile.RUN)

    def get_lines(self):
        for tool in self.components:
            line = ""
            if tool.get_to() is not None:
                line = "curl -sLf {} -o {}".format(tool.get_from(), tool.get_to())
            else:
                line = "curl -sLf {} -o /bin/{} && chmod 755 /bin/{}".format(tool.get_from(), tool.get_name(), tool.get_name())
            if tool.get_command() is not None:
                line = line + "; {}".format(tool.get_command().rstrip())
            yield line

class Execute(Command):
    def __init__(self, components):
        Command.__init__(self, components, dockerfile.RUN)

    def get_lines(self):
        return (component.get_command().rstrip() for component in self.components)

class Copy(Command):
    def __init__(self, components):
        Command.__init__(self, components, dockerfile.COPY)

    def get_lines(self):
        for component in self.components:
            if component.get_command() is None:
                yield "{} {}".format(component.get_from(), component.get_to())
            else:
                yield "{} {} {}".format(component.get_command(), component.get_from(), component.get_to())

class Pip(Command):
    def __init__(self, components):
        Command.__init__(self, components, dockerfile.RUN)

    def get_lines(self):
        yield "pip install {}".format(' '.join(self.get_tool_names()))

class Export(Command):
    def __init__(self, components):
        Command.__init__(self, components, dockerfile.ENV)

    def get_lines(self):
        yield ' '.join(self.get_tool_names())

class AddAptGetRepo(Command):
    def __init__(self, components):
        Command.__init__(self, components, dockerfile.RUN)

    def get_lines(self):
        command = [
            'apt-get --yes update && apt-get --yes install lsb-release gnupg apt-transport-https',
        ]
        for component in self.components:
            release_prefix = component.get_release_prefix()
            repo = component.get_repo()
            repo_name = component.get_name()
            repo_url = component.get_repo_url()
            key_url = component.get_key_url()
            keyring = component.get_keyring()
            if repo == "":
                repo = '"{}$(lsb_release -cs)"'.format(release_prefix)
            download_command = [
                'REPO="{}"'.format(repo),
                'echo "deb {} $REPO main" | tee /etc/apt/sources.list.d/{}.list'.format(repo_url, repo_name),
            ]
            if keyring == "":
                download_command.append('curl -sL {} | apt-key add -'.format(key_url))
            else:
                download_command.append('curl -sL {} | apt-key --keyring {} add -'.format(key_url, keyring))
            command.extend(download_command)

        command.extend([
            "apt-get --yes --purge remove lsb-release gnupg apt-transport-https",
            "rm -rf /var/lib/apt/lists"
        ])
        return (line for line in command)

class Git(Command):
    def __init__(self, components):
        Command.__init__(self, components, dockerfile.RUN)

    def get_lines(self):
        command_lines = []
        for component in self.components:
            command_lines.append("git -c http.sslVerify=false clone {} {}".format(component.get_from(), component.get_to()))
            if component.version is not None:
                command_lines.append('git -C {} checkout {}'.format(component.get_to(), component.get_version()))
        return (line for line in command_lines)


class InfoGenerator:
    def __init__(self, commands):
        self.commands = commands

    def generate_help_command_info(self):
        apt_get_commands = []
        pip_commands = []
        downloaded_commands = []

        for command in self.commands:
            if isinstance(command, AptGet):
                apt_get_commands.extend(InfoGenerator._get_package_name_and_bins(command))
            if isinstance(command, Pip):
                pip_commands.extend(InfoGenerator._get_package_name_and_bins(command))
            if isinstance(command, (Curl, Git, Execute, Copy)):
                command_tools = command.get_tools()
                for tool in command_tools:
                    if tool.get_info() is not None:
                        downloaded_commands.append((tool.get_name(), tool.get_version(), tool.get_info()))

        command_config= {
            "apt": apt_get_commands,
            "pip": pip_commands,
            "downloaded": downloaded_commands,
        }

        return json.dumps(command_config)


    def generate_welcome_message(self):
        basic_tools = []
        custom_shell_commands = []
        exported_environments = []
        for command in self.commands:
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

    @staticmethod
    def _get_package_name_and_bins(command):
        command_tools = command.get_tools()
        to_return = []
        for tool in command_tools:
            name = tool.get_name()
            binaries = tool.get_provided_apps()
            to_return.append((name, binaries))
        return to_return

class CommandFactory:
    @staticmethod
    def create(config):
        name = list(config.keys())[0]
        pair = registry.get(name)
        if pair is None:
            print("{} is not a supported dockerfile config command".format(name))
            exit(1)
        command_class = pair[0]
        component_classes = list(pair[1])
        component_parser = components.ComponentConfigParser(*component_classes)
        parsed_components = component_parser.parse_components(config[name])
        instance = command_class(parsed_components)
        return instance

class CommandRegistry:
    def __init__(self):
        self._registry = dict()

    def register_command(self, name, command_class, *argv):
        self._registry[name] = (command_class, list(argv))

    def get(self, name):
        return self._registry.get(name)


registry = CommandRegistry()
registry.register_command("apt-get", AptGet, components.StringComponentConfig, components.DictComponentConfig)
registry.register_command("curl", Curl, components.ToolConfig)
registry.register_command("bash", Execute, components.BashCommandConfig)
registry.register_command("copy", Copy, components.ToolConfig)
registry.register_command("pip", Pip, components.StringComponentConfig, components.DictComponentConfig)
registry.register_command("env", Export, components.StringComponentConfig)
registry.register_command("add-apt-repo", AddAptGetRepo, components.AptRepoConfig)
registry.register_command("git", Git, components.ToolConfig)

