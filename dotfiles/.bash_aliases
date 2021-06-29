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

##################
# COLORS & CHARS #
##################

# rendition parameters, see http://conemu.github.io/en/AnsiEscapeCodes.html
export SGR_RESET="\033[0m"
export SGR_BOLD="\033[1m"
export SGR_BOLD_UNSET="\033[22m"
export SGR_DIM="\033[2m"
export SGR_DIM_UNSET="\033[22m"
export SGR_ITALIC="\033[3m"
export SGR_ITALIC_UNSET="\033[23m"
export SGR_UNDERLINE="\033[4m"
export SGR_UNDERLINE_UNSET="\033[24m"
export SGR_INVERSE="\033[7m"
export SGR_INVERSE_UNSET="\033[27m"

# ansi colors, see https://en.wikipedia.org/wiki/ANSI_escape_code#Colors
# pick of solarized color theme working fine with light and dark background, see http://ethanschoonover.com/solarized
# only available when tput is available, otherwise fall-back to 16 colors (ansi escape codes)
if tput setaf 1 &> /dev/null; then
  export COLOR_LIGHT_GRAY=$(tput setaf 244) # called base0 in solarized color theme (default color for dark theme)
  export COLOR_DARK_GRAY=$(tput setaf 241)  # called base00 in solarized color theme (default color for light theme)
  export COLOR_YELLOW=$(tput setaf 136);
  export COLOR_ORANGE=$(tput setaf 166);
  export COLOR_RED=$(tput setaf 160);
  export COLOR_MAGENTA=$(tput setaf 125);
  export COLOR_VIOLET=$(tput setaf 61);
  export COLOR_BLUE=$(tput setaf 33);
  export COLOR_CYAN=$(tput setaf 37);
  export COLOR_GREEN=$(tput setaf 64);
else
  export COLOR_LIGHT_GRAY="\033[37m"
  export COLOR_DARK_GRAY="\033[90m"
  export COLOR_YELLOW="\033[33m"
  export COLOR_ORANGE="\033[91m"
  export COLOR_RED="\033[31m"
  export COLOR_MAGENTA="\033[35m"
  export COLOR_VIOLET="\033[94m"
  export COLOR_BLUE="\033[34m"
  export COLOR_CYAN="\033[36m"
  export COLOR_GREEN="\033[32m"
fi;

# color given text in given rendition/color
function color() {
  local rendition=""
  local color="$1"
  [[ $color == bold_* ]]      && rendition=$SGR_BOLD      && color=${color#*_}
  [[ $color == dim_* ]]       && rendition=$SGR_DIM       && color=${color#*_}
  [[ $color == italic_* ]]    && rendition=$SGR_ITALIC    && color=${color#*_}
  [[ $color == underline_* ]] && rendition=$SGR_UNDERLINE && color=${color#*_}
  [[ $color == inverse_* ]]   && rendition=$SGR_INVERSE   && color=${color#*_}
  case "$color" in
    "light_gray") color=$COLOR_LIGHT_GRAY;;
    "dark_gray")  color=$COLOR_DARK_GRAY;;
    "yellow")     color=$COLOR_YELLOW;;
    "orange")     color=$COLOR_ORANGE;;
    "red")        color=$COLOR_RED;;
    "magenta")    color=$COLOR_MAGENTA;;
    "violet")     color=$COLOR_VIOLET;;
    "blue")       color=$COLOR_BLUE;;
    "cyan")       color=$COLOR_CYAN;;
    "green")      color=$COLOR_GREEN;;
  esac
  if tty -s; then
    echo -e "${rendition}${color}${@:2}${SGR_RESET}"
  else
    echo "${@:2}"
  fi
}

# color given notifications
function debug() {
  echo -e "$(color light_gray $@)"
}

function info() {
  echo -e "$(color cyan $@)"
}

function ok() {
  echo -e "$(color green $@)"
}

function warning() {
  echo -e "$(color orange $@)"
}

function error() {
  echo -e "$(color red $@)"
}

function fatal() {
  echo -e "$(color inverse_red $@)"
}

# show warning message and abort execution
function abort() {
  warning "$@"
  exit 100 # suggested exit code (to be used by trap handler to detect abortion if implemented)
}

# show error message and fail execution
function fail() {
  error "$@"
  exit 1 # default exit code
}

# alignment echo functions
function left() {
  local width="${1}"
  local text="${@:2}"
  printf "%-${width}s" "${text}"
}

function right() {
  local width="${1}"
  local text="${@:2}"
  printf "%+${width}s" "${text}"
}

function center() {
  local width="${1}"
  local text="${@:2}"
  local text_wo_escape_chars="$(echo ${text} | sed -r "s/\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[m|K]//g")"
  local pre_padding=$(((${width}-${#text_wo_escape_chars})/2))
  local post_padding=$((${width}-${#text_wo_escape_chars}-${pre_padding}))
  printf "%*.*s%s%*.*s" ${pre_padding} ${pre_padding} " " "${text}" ${post_padding} ${post_padding} " "
}

# line
line() {
  local width="${1}"
  local char="${2:- }"
  printf "%${width}s" | sed -r "s/ /$char/g"
}

# ruler
function hr() {
  local width="${1:-80}"
  local char="${2:-$(printf "\e(0\x71\e(B")}"
  debug "\n$(line "$width" "$char")\n"
}

# box (centering text)
box()
{
  local width="$((${1}-2+${2}*2))"
  local padding="${2}"
  local margin="${3}"
  local text="${@:4}"
  local text_wo_escape_chars="$(echo ${text} | sed -r "s/\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[m|K]//g")"
  if (( ${#text_wo_escape_chars} > ${width} )); then
    width=${#text_wo_escape_chars}
  fi
  local width="$((${width}+${padding}*2))"
  local dash="$(printf "\e(0q\e(B")"
  for (( i=1; i <= ${margin}; i++ )); do printf "\n"; done
  printf "$(line $margin)\e(0l\e(B$(line "${width}" "${dash}")\e(0k\e(B\n"
  for (( i=1; i <= ${padding}; i++ )); do printf "$(line $margin)\e(0x\e(B$(center "${width}")\e(0x\e(B\n"; done
  printf "$(line $margin)\e(0x\e(B$(center "${width}" "${text}")\e(0x\e(B\n"
  for (( i=1; i <= ${padding}; i++ )); do printf "$(line $margin)\e(0x\e(B$(center "${width}")\e(0x\e(B\n"; done
  printf "$(line $margin)\e(0m\e(B$(line "${width}" "${dash}")\e(0j\e(B\n"
  for (( i=1; i <= ${margin}; i++ )); do printf "\n"; done
}

# show colors
function colors() {
  printf " %-10s  %-10s  %-10s  %-10s  %-10s  %-10s \n" "NORMAL" "BOLD" "DIM" "ITALIC" "UNDERLINE" "INVERSE"
  for i in $(seq 1 72); do printf "\e(0\x71\e(B"; done; printf "\n"
  for color in LIGHT_GRAY DARK_GRAY YELLOW ORANGE RED MAGENTA VIOLET BLUE CYAN GREEN; do
    printf "$SGR_RESET$(eval printf "\$COLOR_$color") %-10s $SGR_RESET" $color
    printf "$SGR_BOLD$(eval printf "\$COLOR_$color") %-10s $SGR_BOLD_UNSET" $color
    printf "$SGR_DIM$(eval printf "\$COLOR_$color") %-10s $SGR_DIM_UNSET" $color
    printf "$SGR_ITALIC$(eval printf "\$COLOR_$color") %-10s $SGR_ITALIC_UNSET" $color
    printf "$SGR_UNDERLINE$(eval printf "\$COLOR_$color") %-10s $SGR_UNDERLINE_UNSET" $color
    printf "$SGR_INVERSE$(eval printf "\$COLOR_$color") %-10s $SGR_INVERSE_UNSET" $color
    printf "$SGR_RESET\n"
  done

  echo
  echo "Log debug msg:   $(debug This is a debug line of text.)"
  echo "Log info msg:    $(info This is an info line of text.)"
  echo "Log ok msg:      $(ok Here everything went ok.)"
  echo "Log warning msg: $(warning Oh, something went wrong and requires a warning.)"
  echo "Log error msg:   $(error Now we have an error.)"
  echo "Log fatal msg:   $(fatal Wow, that is fatal.)"
}

# show box characters
function box_chars() {
  char=( 6a 6b 6c 6d 6e 71 74 75 76 77 78 )
  for i in ${char[*]}
  do
    printf "0x$i \x$i \e(0\x$i\e(B\n"
  done
}

# clear screen
alias c='clear'

###########
# FINDERS #
###########

# find alias (-a), built-in (-b), command (-c) and function (-A function)
function fa() {
  commands=($(compgen -abcA function $1 | sort -u))
  for command in ${commands[@]}; do
    details="$(alias | grep -E "^alias $command=" | cut -c 7-)"
    if [ -z "$details" ]; then
      details="$(declare -f $command)"
    fi
    if [ -z "$details" ]; then
      details="$command"
    fi
    echo "$details" | grep --color -E "^$command|$"
  done
}

# find history entries
alias h='history'
alias fh='h | grep'

# find files and directories
function ff() {
  # note: user must prevent globbing via eascaping: \*
  find_term="$1"
  find_term="${find_term/^/}"
  find_term="${find_term/$/}"
  grep_term="$1"
  grep_term="${grep_term/^/\/}"
  find -L . -iname "*$find_term*" 2>/dev/null | grep -i "$grep_term"
}
function fd() {
  # note: user must prevent globbing via eascaping: \*
  find_term="$1"
  find_term="${find_term/^/}"
  find_term="${find_term/$/}"
  grep_term="$1"
  grep_term="${grep_term/^/\/}"
  find -L . -type d -iname "*$find_term*" 2>/dev/null | grep -i "$grep_term"
}

# find open files and ports
alias fof='lsof'
alias fop='lsof -i'

##########
# BASICS #
##########

# cd into the dotfiles
alias dot='cd $DOTFILES_HOME'

# become root
alias root='sudo -i'

# backup file
function bak() {
  bak=$1.$(date +%Y%m%d-%H%M).bak
  cp -p -r $1 $bak
  echo "Backed up $1 to $bak"
}

# make mkdir create parent folders as well
alias mkdir='mkdir -p'

# convenient directory up traversal
alias cd..='cd ..'
alias ..='cd ..'
function create_directory_traversal_aliases() {
  local dotSlash=""
  local baseName=""
  for i in 1 2 3 4 5 6 7 8 9
  do
    dotSlash=${dotSlash}'../';
    baseName="..${i}"
    alias $baseName="cd ${dotSlash}"
    baseName="${i}.."
    alias $baseName="cd ${dotSlash}"
  done
}
create_directory_traversal_aliases
unset create_directory_traversal_aliases

# watch/loop command(s)
alias watch='watch --interval 1 --differences --color --no-title ' # trailing space is important for consecutive alias expansion, see http://unix.stackexchange.com/questions/25327/watch-command-alias-expansion
function loop() {
  let i=0
  while true; do
    let i++
    echo -e "[$(color green INVOCATION:) $(color red $i)]"
    eval "$*"
    sleep 1
  done
}

# url conversion
function urlencode() {
    local length="${#1}"
    for (( i = 0; i < length; i++ )); do
        local c="${1:i:1}"
        case $c in
            [a-zA-Z0-9.~_-]) printf "$c" ;;
            *) printf '%%%02X' "'$c"
        esac
    done
}
function urldecode() {
    local url_encoded="${1//+/ }"
    printf '%b' "${url_encoded//%/\\x}"
}

# base64 conversion
function base64encode() {
  base64 <(echo "$*")
}
function base64decode() {
  base64 -d <(echo "$1")
}

# date/time conversion
function tosecs() {
  date -d "$*" +"%s"
}
function todate() {
  date -d @$1 -u +"%Y-%m-%d %H:%M:%S %z"
}

# set time manually (in case of ntp issues)
alias settime='sudo date -s "$(date --date="$(curl -sI www.google.com 2>&1 | sed -n -r "s/Date: (.*)/\1/1p")")"'

# image resizing
alias shrink='sips -Z 1024'

#########
# TOOLS #
#########

# vi
alias vi='vim'

# grep
alias grep='grep --color'

# git
alias g='git'
function clone() {
  if [[ $1 == http* ]] || [[ $1 == git* ]]; then
    for repo_url in "$@"; do
      git clone -c http.sslVerify=false --recursive "$repo_url"
    done
  else
    owner="$1"
    repo="$2"
    git clone -c http.sslVerify=false --recursive https://github.com/$owner/$repo.git
  fi
}
function commit() {
  GIT_COMMITTER_NAME="$USER_NAME" GIT_COMMITTER_EMAIL="$USER_EMAIL" git commit --author="$USER_NAME <$USER_EMAIL>" "$@"
}
function push() {
  # check for git repo
  if [[ ! -d ".git" ]]; then
    echo "This directory holds no git repo. Are you in the wrong directory?"
    return
  fi

  # show changes to user, ask for confirmation and commit and push if approved
  git status
  git add --patch # ask for confirmation of individual hunks and deletions
  git add . --all # auto-stage all new/removed files
  git status
  read -p "[Commit Message / Final Confirmation] Describe your change: " msg
  if [ -z "$msg" ]; then
    commit -m "Update"
  else
    commit -m "$msg"
  fi
  git push origin HEAD
}
alias pull='git pull'
alias gitk='git log --oneline --graph --decorate --all'

# ps
alias p='ps -ef'
alias pp='pstree' # no forest option in ps

# ls
alias l='LC_COLLATE=C ls -ACF --group-directories-first'     # all files but .&.., wide/columns, classifier, sorted by dirs only
alias ll='LC_COLLATE=C ls -alF --group-directories-first'    # all files, long, classifier, sorted by dirs only
alias lll='LC_COLLATE=C ls -alFtr --group-directories-first' # all files, long, classifier, sorted by dirs, then time (reverse)

# tree
alias tree='tree -a' # include hidden files by default

# tar
alias tarup='tar -cvf'
alias untar='tar -xvf'

# disk usage
function du() {
  $(which du) -h -d 1 "$@" | sort -h
}
function df() {
  $(which df) -h "$@" | sort -h -k 6
}

alias ag='ag --all-types --hidden'

# iptables
alias ipt='iptables'
alias iptlist='ipt -L -n -v --line-numbers'
alias iptlistin='ipt -L INPUT -n -v --line-numbers'
alias iptlistout='ipt -L OUTPUT -n -v --line-numbers'
alias iptlistfw='ipt -L FORWARD -n -v --line-numbers'

# tcpdump
alias tcpd='tcpdump -l -s 0'

# parallel shell (list hosts with -h and use -i or -o and -e options to see the output)
alias parallelssh='pssh -i -p 10 -O LogLevel=fatal -O StrictHostKeyChecking=no -O UserKnownHostsFile=/dev/null'

function make_sudoer() {
  local user_name="$1"

  # check for user name
  if [[ -z "$user_name" ]]; then
    error "No user name provided!"
    return 1
  fi

  # grant sudo privileges to user
  echo "$user_name ALL=(root) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/10-"$user_name" > /dev/null
  sudo chmod 0440 /etc/sudoers.d/10-"$user_name"
}

# ssh
alias hosts='cat ~/.ssh/config | grep -E "^(# .*Hosts|Host [^*])" | sed "s/# \(.*\)/\1/g" | sed "s/^Host /- /g"'

# name this host in terms of the dotfiles (will be evaluated by the prompt)
function name() {
  local name="$1"
  name=${name##*@} # strip of user (in case this is an ssh host)
  name=${name%%:*} # strip of port (in case this is an ssh host)
  echo $name > "$DOTFILES_HOME/.host_alias"
  source $DOTFILES_HOME/.bash_prompt
}

# fuse
function fuse() {
  # get address and folder right
  address="$1"
  if [[ ! "$address" == *:* ]]; then
    address="$address:"
  fi
  folder="${1//\//\\}"
  folder="${folder%\\}"
  # check whether we should mount or unmount the file system based on present state
  if [[ ! -d ~/fuse/$folder ]]; then
    mkdir -p ~/fuse/"$folder" 1> /dev/null && sshfs $address ~/fuse/"$folder" 1> /dev/null && echo "Mounted successfully: ~/fuse/$folder" && return 0
  else
    [[ $(ls ~/fuse/"$folder" 2> /dev/null) ]] && umount -f ~/fuse/"$folder" 1> /dev/null
    rm -d ~/fuse/"$folder" 1> /dev/null && echo "Unmounted successfully: ~/fuse/$1" && return 0
  fi
  echo "Operation failed!" && [[ ! $(ls -A ~/fuse/"$folder" 2>/dev/null) ]] && rm -d ~/fuse/"$folder"
}

# tmux
function ts() {
  cp -f "$DOTFILES_HOME/.tmux.conf" "/tmp/.tmux.$DOTFILES_USER.conf"
  local session="$1"; local detach=""; [[ "$1" == "-d" ]] && detach="-d" && session="${@:2}"; session=${session:-default}
  echo -n "Creating new $session session: "
  tmux -S "/tmp/.tmux.$DOTFILES_USER.socket" -f "/tmp/.tmux.$DOTFILES_USER.conf" new-session $detach -s "$session"
}
function ta() {
  if [[ -z "$1" ]]; then
    if [[ -n "$TMUX" ]]; then
      # show what would be called effectively (to let others without this environment work with it)
      session="$(tmux -S "/tmp/.tmux.$DOTFILES_USER.socket" display-message -p "#S" 2>/dev/null | sed -r "s/^0$//p")"
      echo "Full command: tmux -S /tmp/.tmux.$DOTFILES_USER.socket attach-session -t ${session:-<session>}"
    else
      if [[ $(tmux -S /tmp/.tmux.$DOTFILES_USER.socket ls 2>/dev/null | grep -E "^default:.*$") ]]; then
        echo -n "Attaching to default session: "
        tmux -S /tmp/.tmux.$DOTFILES_USER.socket attach-session -t "default"
      else
        ts
      fi
    fi
  else
    echo -n "Attaching to $1 session: "
    tmux -S /tmp/.tmux.$DOTFILES_USER.socket attach-session -t "$1"
  fi
}
function tk() {
  if [[ -z "$1" ]]; then
    tmux -S "/tmp/.tmux.$DOTFILES_USER.socket" ls | grep -F : | awk -F':' '{print $1}' | xargs -i tmux -S /tmp/.tmux.$DOTFILES_USER.socket kill-session -t {}
  else
    tmux -S /tmp/.tmux.$DOTFILES_USER.socket kill-session -t "$1"
  fi
}
alias tls='tmux -S "/tmp/.tmux.$DOTFILES_USER.socket" ls 2>&1 | grep -v "failed to connect to server"'

######################
# CLOUD & CONTAINERS #
######################

# terraform
unset TF_LOG # export TF_LOG=INFO # one of: TRACE, DEBUG, INFO, WARN or ERROR
alias tf='terraform'
alias tfa='tf apply'
alias tfg='tf graph -draw-cycles -module-depth=99 | dot -Tpng > /tmp/graph.png | eog /tmp/graph.png' # unfortunately <() isn't working here
alias tfp='tf plan -module-depth=99'
alias tfr='tf refresh'
alias tfs='tf show -module-depth=99'
alias tft='tf taint'

# docker
alias d='docker'

# kubernetes
alias s='systemctl'
alias j='journalctl'
function ksn() {
  export DOTFILES_KUBECTL_NAMESPACE="$1"
}
function k() {
  if [[ -z $DOTFILES_KUBECTL_NAMESPACE ]]; then
    kubectl "$@"
  else
    kubectl --namespace=$DOTFILES_KUBECTL_NAMESPACE "$@"
  fi
}
alias kd='kubectl --namespace=default'
alias ks='kubectl --namespace=kube-system'
alias ka='kubectl --all-namespaces=true'
