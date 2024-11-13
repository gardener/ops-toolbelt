# SPDX-FileCopyrightText: 2024 SAP SE or an SAP affiliate company and Gardener contributors
#
# SPDX-License-Identifier: Apache-2.0
# shellcheck disable=SC1091 disable=SC2148

# .bash_profile executed by the command interpreter for bash login shells

# default DOTFILES_USER if not set
[[ -z "$DOTFILES_USER" ]] && export DOTFILES_USER="${DOTFILES_USER:-$(whoami)}"

# default DOTFILES_HOME if not set
if [[ -z "$DOTFILES_HOME" ]]; then
    export DOTFILES_HOME
    DOTFILES_HOME="$(dirname "$(realpath "$(readlink -f "${BASH_SOURCE[0]}")")")"
fi

# source default .bashrc
[[ -s "$DOTFILES_HOME/.bashrc" ]] && source "$DOTFILES_HOME/.bashrc"
