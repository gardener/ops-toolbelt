if ! [ $(id -u) = 0 ]; then
    echo "running as non-root and crictl will not be installed"
    exit 0
fi

if [ -x "$(command -v crictl)" ]; then
  rm -rf /etc/crictl.yaml
  cp /root/dotfiles/crictl.yaml /etc/crictl.yaml
  exit 0
fi

VERSION="v1.17.0"
curl -fsSLO https://github.com/kubernetes-sigs/cri-tools/releases/download/$VERSION/crictl-$VERSION-linux-amd64.tar.gz
tar zxvf crictl-$VERSION-linux-amd64.tar.gz -C /usr/local/bin
rm -f crictl-$VERSION-linux-amd64.tar.gz
rm -rf /etc/crictl.yamls
cp /root/dotfiles/crictl.yaml /etc/crictl.yaml