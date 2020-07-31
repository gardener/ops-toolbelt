## Ops Toolbelt


### What is the ops-toolbelt
The `ops-toolbelt` aims to be a standard operator container image with pre-installed useful tools for troubleshooting issues on gardener landscapes. The `ops-toolbelt` images can be used by the Gardener Dashboard web consoles functionality to log into the garden, seed, or shoot clusters.

The pods created with this image can be both general pods and node-bound pods (behaving as if being on the node directly)
Starting a pod with the ops-toolbel timage requires a running Kubelet and healthy control plane, a working VPN connection, and sufficient capacity on the node.


### Usage

#### Running a container locally
The simplest way of using the `ops-toolbelt` is to just run the following command:
```bash
$ docker run -it eu.gcr.io/gardener-project/gardener/ops-toolbelt-gardenctl:latest

Ubuntu 18.04.2 LTS \n \l

This container comes with the following preinstalled tools:
curl git tree silversearcher-ag htop less vim tmux bash-completion dnsutils netcat-openbsd iproute2 dstat ngrep tcpdump python-minimal jq yaml2json kubectl pip cat mdv awscli azure-cli python-novaclient python-glanceclient python-cinderclient python-swiftclient google-cloud-sdk aliyun-cli gardenctl

The sourced dotfiles are located under /root/dotfiles.
Additionally you can add your own personal git settings in /root/dotfiles/.config/git/config_personal

There is an operations guide which can be useful when troubleshooting gardener issues.
It can be found under /guide the documents from it can be read with either cat or mdv.
Additionally, there is a /hacks directory containing useful scripts. Execute ls /hacks to see what is available.

The following variables have been exported:
DOTFILES_USER=root DOTFILES_HOME=/root/dotfiles
```

You can then add personal configurations to your `ops-toolbelt` container for tools like `kubectl`, `gardenctl`, `gcloud` and so on ...

#### Running the ops-toolblet as privileged pod on a node
Get the names of the nodes on your cluster and then run `hacks/ops-pod` with the node you want to start the pod on:
```bash
$ kubectl get nodes
NAME                                            STATUS   ROLES    AGE    VERSION
node1   Ready    <none>   56d    v1.11.10-gke.5
node2   Ready    <none>   72d    v1.11.10-gke.5
node3   Ready    <none>   150d   v1.11.10-gke.5

$ ./hacks/ops-pod node1
node name provided ...
Deploying ops pod on node1

pod/ops-pod created
Waiting for pod to be running...
Waiting for pod to be running...
This container comes with the following preinstalled tools:
curl git tree silversearcher-ag htop less vim tmux bash-completion dnsutils netcat-openbsd iproute2 dstat ngrep tcpdump python-minimal jq yaml2json kubectl pip cat mdv

The sourced dotfiles are located under /root/dotfiles.
Additionally you can add your own personal git settings in /root/dotfiles/.config/git/config_personal

The following variables have been exported:
DOTFILES_USER=root DOTFILES_HOME=/root/dotfiles

root at node1 in /
$
```

Use `./hacks/ops-pod --help` to check what other options are available


### Building ops-toolbelt images
Dockerfiles for the images are generated from files in the `dockerfile-config` directory.

To build all pre-configured images run:
```bash
$ .ci/build
```

### Known issues
1. Currently there's a known issue when using `/bin/sh`. We implemented a color scheme and also added some helper function to display in `/bin/bash` terminal which doesn't work in `/bin/sh`. As workaround when you want to use some script which by default needs to utilize `/bin/sh` please use `/bin/bash` instead if possible: (take `chroot` for example)
```bash
$ chroot /some_dir /bin/bash
```
