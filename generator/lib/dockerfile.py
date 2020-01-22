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

RUN = "run"
COPY = "copy"
ENV = "env"

class Dockerfile:
    def __init__(self, from_image, commands):
        self.from_image = "FROM {}\n".format(from_image)
        self.commands = commands
        self.layers = []

    def create(self):
        for command in self.commands:
            if command.dockerfile_instruction == COPY:
                for line in command.get_lines():
                    self.layers.append(DockerLayer(command.dockerfile_instruction))
                    self.layers[-1].append(line)
            else:
                if len(self.layers) == 0 or not self.layers[-1].supports_command_instruction(command.dockerfile_instruction):
                    self.layers.append(DockerLayer(command.dockerfile_instruction))
                for line in command.get_lines():
                    self.layers[-1].append(line)

    def to_string(self):
        output = self.from_image
        for layer in self.layers:
            output += layer.get_layer_as_string()
        return output

    def add_welcome_message(self, title):
        self.layers.append(DockerLayer(RUN, False))
        self.layers[-1].append("""echo 'printf ${{COLOR_GREEN}}; figlet {}; printf ${{SGR_RESET}}' >> /root/.bashrc;\\
    echo 'echo \\n' >> /root/.bashrc;\\
    echo "echo Run \\$(color orange 'ghelp') to get information about installed tools and packages"  >> /root/.bashrc
""".format(title))

    def add_ghelp_info(self, ghelp_info):
        self.layers.append(DockerLayer(RUN, False))
        self.layers[-1].append(
            """echo '{}' > /var/lib/ghelp_info""".format(ghelp_info)
        )

class DockerLayer:
    def __init__(self, instruction, reindent_string_output=True):
        self.instruction = instruction
        self.commands = []
        self.reindent_string_output = reindent_string_output

    def supports_command_instruction(self, instruction):
        if instruction == COPY:
            return False
        else:
            return self.instruction == instruction

    def append(self, command):
        if len(self.commands) != 0:
            self.commands[-1] += ";\\\n"
        self.commands.append(command)

    def get_layer_as_string(self):
        output = self.instruction + " "

        for command in self.commands:
            output += command
        if self.reindent_string_output:
            return self.reindent(output)
        return output

    @staticmethod
    def reindent(command):
        command_lines = command.split('\n')
        command_lines = command_lines[:1] + [(4 * ' ') + command_line.lstrip() for command_line in command_lines[1:]]
        return '\n'.join(command_lines) + '\n'