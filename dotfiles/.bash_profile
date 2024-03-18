# SPDX-FileCopyrightText: 2024 SAP SE or an SAP affiliate company and Gardener contributors
#
# SPDX-License-Identifier: Apache-2.0

# .bash_profile executed by the command interpreter for bash login shells

# default DOTFILES_USER if not set
[[ -z "$DOTFILES_USER" ]] && export DOTFILES_USER="${DOTFILES_USER:-$(whoami)}"

# default DOTFILES_HOME if not set
[[ -z "$DOTFILES_HOME" ]] && export DOTFILES_HOME="$(dirname "$(realpath "$(readlink -f "${BASH_SOURCE[0]}")")")"

# source default .bashrc
[[ -s "$DOTFILES_HOME/.bashrc" ]] && source "$DOTFILES_HOME/.bashrc"
