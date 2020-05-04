if ! [ $(id -u) = 0 ]; then
    echo "running as non-root and crictl will not be installed"
    exit 0
fi

if [ -x "$(command -v crictl)" ]; then
rm -rf /etc/crictl.yaml
tee /etc/crictl.yaml << EOT
  runtime-endpoint: unix:///run/containerd/containerd.sock
  image-endpoint: unix:///run/containerd/containerd.sock
  timeout: 10
EOT
exit 0
fi

VERSION="v1.17.0"
curl -fsSLO https://github.com/kubernetes-sigs/cri-tools/releases/download/$VERSION/crictl-$VERSION-linux-amd64.tar.gz
tar zxvf crictl-$VERSION-linux-amd64.tar.gz -C /usr/local/bin
rm -f crictl-$VERSION-linux-amd64.tar.gz
rm -rf /etc/crictl.yaml
tee /etc/crictl.yaml << EOT
runtime-endpoint: unix:///run/containerd/containerd.sock
image-endpoint: unix:///run/containerd/containerd.sock
timeout: 10
EOT