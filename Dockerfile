FROM ubuntu:22.04
run apt-get --yes update && apt-get --yes install curl tree vim-tiny htop less tmux bash-completion python3-distutils dstat ngrep iotop iftop jq figlet tcpdump sysstat iputils-ping silversearcher-ag iproute2 dnsutils netcat-openbsd python3-minimal locales;\
    rm -rf /var/lib/apt/lists;\
    curl -sLf https://github.com/bronze1man/yaml2json/releases/download/v1.3/yaml2json_linux_amd64 -o /bin/yaml2json && chmod 755 /bin/yaml2json;\
    curl -sLf https://raw.githubusercontent.com/johanhaleby/kubetail/master/kubetail -o /bin/kubetail && chmod 755 /bin/kubetail;\
    curl -sLf https://github.com/containerd/nerdctl/releases/download/v0.22.0/nerdctl-0.22.0-linux-amd64.tar.gz -o /nerdctl.tar.gz; tar Cxzvvf /usr/local/bin nerdctl.tar.gz &&\
    rm -f nerdctl.tar.gz &&\
    mkdir /etc/nerdctl &&\
    echo address = \"unix:///host/run/containerd/containerd.sock\" >> /etc/nerdctl/nerdctl.toml &&\
    echo namespace = \"k8s.io\" >> /etc/nerdctl/nerdctl.toml;\
    curl -sLf https://storage.googleapis.com/kubernetes-release/release/v1.24.3/bin/linux/amd64/kubectl -o /bin/kubectl && chmod 755 /bin/kubectl;\
    locale-gen "en_US.UTF-8";\
    rm -f /var/cache/apt/archives/*.deb /var/cache/apt/archives/partial/*.deb /var/cache/apt/*.bin || true
env LANG=en_US.UTF-8 LANGUAGE=en_US.UTF-8
copy ./dotfiles /root/dotfiles
copy ./hacks /hacks
run echo "" >> /root/.bashrc;\
    echo "source /etc/profile.d/bash_completion.sh" >> /root/.bashrc;\
    echo "source /root/dotfiles/.install_on_demand/.table" >> /root/dotfiles/.bashrc;\
    echo "source /root/dotfiles/.install_on_demand/.wireguard" >> /root/dotfiles/.bashrc;\
    echo "" >> /root/.bashrc;\
    echo "# source bashrc from dotfiles" >> /root/.bashrc;\
    echo "source /root/dotfiles/.bashrc" >> /root/.bashrc;\
    touch /root/dotfiles/.config/git/config_personal;\
    echo "export PATH=/hacks:\$PATH" >> /root/.bashrc
env DOTFILES_USER=root DOTFILES_HOME=/root/dotfiles
run echo 'printf ${COLOR_GREEN}; figlet gardener shell; printf ${SGR_RESET}' >> /root/.bashrc;\
    echo 'echo \n' >> /root/.bashrc;\
    echo "echo Run \$(color orange 'ghelp') to get information about installed tools and packages"  >> /root/.bashrc
run echo '{"apt": [["curl", "curl"], ["tree", "tree"], ["vim-tiny", "vim-tiny"], ["htop", "htop"], ["less", "less"], ["tmux", "tmux"], ["bash-completion", "bash-completion"], ["python3-distutils", "python3-distutils"], ["dstat", "dstat"], ["ngrep", "ngrep"], ["iotop", "iotop"], ["iftop", "iftop"], ["jq", "jq"], ["figlet", "figlet"], ["tcpdump", "tcpdump"], ["sysstat", "sysstat"], ["iputils-ping", "iputils-ping"], ["silversearcher-ag", "ag"], ["iproute2", "ip"], ["dnsutils", ["delv", "dig", "mdig", "nslookup", "nsupdate"]], ["netcat-openbsd", "netcat"], ["python3-minimal", "python3"]], "pip": [["mdv", "mdv"], ["tabulate", "tabulate"]], "downloaded": [["yaml2json", "v1.3", "transform yaml string to json string without the type infomation."], ["kubetail", null, "Bash script that enables you to aggregate (tail/follow) logs from multiple pods into one stream"], ["nerdctl", "0.22.0", "nerdctl is a Docker-compatible CLI for containerd. The root directory of the host has to be mounted under `/host`"], ["kubectl", "v1.24.3", "command line tool for controlling Kubernetes clusters."], ["table", null, "Helpful tool that can be used to simplify the analysis of iptables entries. Pass a string argument to filter the output via grep."], ["wg", null, "Command line tool for the wireguard VPN."], ["dotfiles", null, "Directory containing the currently active (sourced) dotfiles."]]}' > /var/lib/ghelp_info
