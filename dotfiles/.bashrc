# SPDX-FileCopyrightText: 2024 SAP SE or an SAP affiliate company and Gardener contributors
#
# SPDX-License-Identifier: Apache-2.0

# .bashrc executed by the command interpreter for bash non-login shells

# don't do anything if not running interactively
case $- in
  *i*) ;;
  *) return;;
esac

# append to the history file, don't overwrite
shopt -s histappend

# enable alias expansion in general, i.e. also for non-interactive shells
shopt -s expand_aliases

# check the window size after each command and, if necessary, update the values of LINES and COLUMNS
shopt -s checkwinsize

# export useful variables
export EDITOR=vi                        # make vi the default editor
export HISTCONTROL=ignoreboth           # don't put duplicate lines or lines starting with space in history
export HISTFILESIZE=2000                # history file size
export HISTSIZE=1000                    # history length
export HISTTIMEFORMAT="[%d.%m %H:%M]  " # alternative history format: export HISTTIMEFORMAT="[%F %H]  "
export TERM='xterm-256color'            # set TERM to 256 color mode
export LESS='-R'                        # show ANSI colors; hint: show line numbers with -N

# override locations of included dot files
export PSQLRC="$DOTFILES_HOME/.psqlrc"
export VIMINIT="source $DOTFILES_HOME/.vimrc"

# set the configuration home for many tools, foremost git, but only when not on the
# local machine where this would be unintended/conflicting with default user configuration
[[ "$DOTFILES_HOME" == */tmp/.dotfiles-$DOTFILES_USER ]] && export XDG_CONFIG_HOME="$DOTFILES_HOME/.config"

# generate personalized git config if missing
get_github_user_attr() {
  local user_data="$(curl -skL https://github.com/api/v3/users/$1)"
  echo $user_data | sed -n -r "s/^.*\"$2\"\s*:\s*\"([^\"]*)\".*$/\1/p"
}

git_config_personal="$DOTFILES_HOME/.config/git/config_personal"
if [[ ! -f "$git_config_personal" ]]; then
  dotfiles_user_name="$(get_github_user_attr $DOTFILES_USER name)"
  dotfiles_user_email="$(get_github_user_attr $DOTFILES_USER email)"
  echo -e "# personal settings" > "$git_config_personal"
  echo -e "[credential]\n  username = $DOTFILES_USER" >> "$git_config_personal"
  [[ -n "$dotfiles_user_name"  ]] && echo -e "[user]\n  name = $dotfiles_user_name"   >> "$git_config_personal"
  [[ -n "$dotfiles_user_email" ]] && echo -e "[user]\n  email = $dotfiles_user_email" >> "$git_config_personal"
fi

mkdir -p "${DOTFILES_HOME}/bin" "${DOTFILES_HOME}/scripts" 
# add bin dir to PATH
[[ -d "$DOTFILES_HOME/bin" ]] && PATH="$DOTFILES_HOME/bin:$PATH"

# add scripts dir to PATH
[[ -d "$DOTFILES_HOME/scripts" ]] && PATH="$DOTFILES_HOME/scripts:$PATH"

# source topic-specific bash completions
source <(kubectl completion bash 2> /dev/null)

# source bash aliases
[[ -s "$DOTFILES_HOME/.bash_aliases" ]] && source "$DOTFILES_HOME/.bash_aliases"

# source bash prompt
[[ -s "$DOTFILES_HOME/.bash_prompt" ]] && source "$DOTFILES_HOME/.bash_prompt"

# add local dir to PATH
export PATH=".:$PATH"

# source nearest .source_me/.activate respectively .deactivate when changing directories
function cd() {
  builtin cd "$@"
  wd="$PWD"
  if [[ -z "$PROMPT_AUTO_SOURCE_PATH" ]] || [[ "$wd" != "$PROMPT_AUTO_SOURCE_PATH"* ]]; then
    [[ -n "$PROMPT_AUTO_SOURCE_PATH" ]] && [[ -f "$PROMPT_AUTO_SOURCE_PATH/.deactivate" ]] && source "$PROMPT_AUTO_SOURCE_PATH/.deactivate"
    unset PROMPT_AUTO_SOURCE_PATH
    while [[ $wd != "/" ]]; do
      if [[ -f "$wd/.source_me" ]]; then
        export PROMPT_AUTO_SOURCE_PATH="$wd" && source "$PROMPT_AUTO_SOURCE_PATH/.source_me"
        break
      elif [[ -f "$wd/.activate" ]]; then
        export PROMPT_AUTO_SOURCE_PATH="$wd" && source "$PROMPT_AUTO_SOURCE_PATH/.activate"
        break
      else
        wd="$(dirname "$wd")"
      fi
    done
  fi
}
