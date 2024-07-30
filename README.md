## Ops Toolbelt

[![REUSE status](https://api.reuse.software/badge/github.com/gardener/ops-toolbelt)](https://api.reuse.software/info/github.com/gardener/ops-toolbelt)

### What is the ops-toolbelt
The `ops-toolbelt` aims to be a standard operator container image with pre-installed useful tools for troubleshooting issues on gardener landscapes. The `ops-toolbelt` images can be used by the Gardener Dashboard web consoles functionality to log into the garden, seed, or shoot clusters.

The pods created with this image can be both general pods and node-bound pods (behaving as if being on the node directly)
Starting a pod with the ops-toolbel timage requires a running Kubelet and healthy control plane, a working VPN connection, and sufficient capacity on the node.


### Usage

#### Running a container locally
The simplest way of using the `ops-toolbelt` is to just run the following command:
```bash
$ docker run -it europe-docker.pkg.dev/sap-se-gcp-k8s-delivery/releases-public/eu_gcr_io/gardener-project/gardener/ops-toolbelt:latest

  __ _  __ _ _ __ __| | ___ _ __   ___ _ __   ___| |__   ___| | |
 / _` |/ _` | '__/ _` |/ _ \ '_ \ / _ \ '__| / __| '_ \ / _ \ | |
| (_| | (_| | | | (_| |  __/ | | |  __/ |    \__ \ | | |  __/ | |
 \__, |\__,_|_|  \__,_|\___|_| |_|\___|_|    |___/_| |_|\___|_|_|
 |___/

Run ghelp to get information about installed tools and packages
```

You can then add personal configurations to your `ops-toolbelt` container for tools like `kubectl`, `gcloud` and so on ...

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
                     _                            _          _ _
  __ _  __ _ _ __ __| | ___ _ __   ___ _ __   ___| |__   ___| | |
 / _` |/ _` | '__/ _` |/ _ \ '_ \ / _ \ '__| / __| '_ \ / _ \ | |
| (_| | (_| | | | (_| |  __/ | | |  __/ |    \__ \ | | |  __/ | |
 \__, |\__,_|_|  \__,_|\___|_| |_|\___|_|    |___/_| |_|\___|_|_|
 |___/

Run ghelp to get information about installed tools and packages

root at ops-pod in /
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
