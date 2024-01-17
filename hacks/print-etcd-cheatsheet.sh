#!/usr/bin/env bash
# Copyright 2023 SAP SE or an SAP affiliate company
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


function get_wrapper_process_id() {
  process_id=$(pgrep wrapper)
  echo "${process_id}"
}

function get_backup_restore_process_id() {
  process_id=$(pgrep etcdbrctl)
  echo "${process_id}"
}

wrapper_pid=$(get_wrapper_process_id)
if [[ -z "$wrapper_pid" ]]; then
	echo "error: cannot find the process id for etcd-wrapper. Please ensure it is running"
	exit 1
fi
backup_restore_pid=$(get_backup_restore_process_id)
if [[ -z "$backup_restore_pid" ]]; then
	echo "error: cannot find the process id for backup-restore. Please ensure it is running"
	exit 1
fi

cat <<EOF
 📌 ETCD PKI resource paths:
  --------------------------------------------------
  --cacert=proc/${wrapper_pid}/root/var/etcd/ssl/client/ca/bundle.crt
  --cert=proc/${wrapper_pid}/root/var/etcd/ssl/client/client/tls.crt
  --key=proc/${wrapper_pid}/root/var/etcd/ssl/client/client/tls.key

 📌 ETCD configuration path:
  --------------------------------------------------
  In etcd-wrapper: proc/${wrapper_pid}/root/home/nonroot/etcd.conf.yaml
  In etcd-backup-restore: proc/${backup_restore_pid}/root/home/nonroot/etcd.conf.yaml

 📌 ETCD data directory:
  --------------------------------------------------
  proc/${wrapper_pid}/root/var/etcd/data

 📌 ETCD maintenance commands:
  --------------------------------------------------
  List all etcd members:
  etcdctl member list -w table \\
  --cacert=proc/${wrapper_pid}/root/var/etcd/ssl/client/ca/bundle.crt \\
  --cert=proc/${wrapper_pid}/root/var/etcd/ssl/client/client/tls.crt \\
  --key=proc/${wrapper_pid}/root/var/etcd/ssl/client/client/tls.key \\
  --endpoints=https://etcd-main-local:2379

  Update etcd member peer URL:
  etcdctl member update <member-id> \\
  --peer-urls=<new-peer-url-to-set> \\
  --cacert=proc/${wrapper_pid}/root/var/etcd/ssl/client/ca/bundle.crt \\
  --cert=proc/${wrapper_pid}/root/var/etcd/ssl/client/client/tls.crt \\
  --key=proc/${wrapper_pid}/root/var/etcd/ssl/client/client/tls.key \\
  --endpoints=https://etcd-main-local:2379

  Get endpoint status for the etcd cluster:
  etcdctl endpoint -w table --cluster status \\
  --cacert=proc/${wrapper_pid}/root/var/etcd/ssl/client/ca/bundle.crt \\
  --cert=proc/${wrapper_pid}/root/var/etcd/ssl/client/client/tls.crt \\
  --key=proc/${wrapper_pid}/root/var/etcd/ssl/client/client/tls.key \\
  --endpoints=https://etcd-main-local:2379

  List all alarms:
  etcdctl alarm list \\
  --cacert=proc/${wrapper_pid}/root/var/etcd/ssl/client/ca/bundle.crt \\
  --cert=proc/${wrapper_pid}/root/var/etcd/ssl/client/client/tls.crt \\
  --key=proc/${wrapper_pid}/root/var/etcd/ssl/client/client/tls.key \\
  --endpoints=https://etcd-main-local:2379

  Disarm all alarms:
  etcdctl alarm disarm \\
  --cacert=proc/${wrapper_pid}/root/var/etcd/ssl/client/ca/bundle.crt \\
  --cert=proc/${wrapper_pid}/root/var/etcd/ssl/client/client/tls.crt \\
  --key=proc/${wrapper_pid}/root/var/etcd/ssl/client/client/tls.key \\
  --endpoints=https://etcd-main-local:2379

  Defragment etcd:
  etcdctl defrag \\
  --cacert=proc/${wrapper_pid}/root/var/etcd/ssl/client/ca/bundle.crt \\
  --cert=proc/${wrapper_pid}/root/var/etcd/ssl/client/client/tls.crt \\
  --key=proc/${wrapper_pid}/root/var/etcd/ssl/client/client/tls.key \\
  --endpoints=https://etcd-main-local:2379

  Change leadership:
  etcdctl move-leader <new-leader-member-id> \\
  --cacert=proc/${wrapper_pid}/root/var/etcd/ssl/client/ca/bundle.crt \\
  --cert=proc/${wrapper_pid}/root/var/etcd/ssl/client/client/tls.crt \\
  --key=proc/${wrapper_pid}/root/var/etcd/ssl/client/client/tls.key \\
  --endpoints=https://etcd-main-local:2379

 📌 ETCD Key-Value commands:
  --------------------------------------------------

  Get key details:
  etcdctl get <key> \\
  --cacert=proc/${wrapper_pid}/root/var/etcd/ssl/client/ca/bundle.crt \\
  --cert=proc/${wrapper_pid}/root/var/etcd/ssl/client/client/tls.crt \\
  --key=proc/${wrapper_pid}/root/var/etcd/ssl/client/client/tls.key \\
  --endpoints=https://etcd-main-local:2379

  Get only value for a given key:
  etcdctl get <key> --print-value-only \\
  --cacert=proc/${wrapper_pid}/root/var/etcd/ssl/client/ca/bundle.crt \\
  --cert=proc/${wrapper_pid}/root/var/etcd/ssl/client/client/tls.crt \\
  --key=proc/${wrapper_pid}/root/var/etcd/ssl/client/client/tls.key \\
  --endpoints=https://etcd-main-local:2379

  List all keys:
  etcdctl get "" --prefix --keys-only \\
  --cacert=proc/${wrapper_pid}/root/var/etcd/ssl/client/ca/bundle.crt \\
  --cert=proc/${wrapper_pid}/root/var/etcd/ssl/client/client/tls.crt \\
  --key=proc/${wrapper_pid}/root/var/etcd/ssl/client/client/tls.key \\
  --endpoints=https://etcd-main-local:2379

  Put a value against a key:
  etcdctl put <key> <value> \\
  --cacert=proc/${wrapper_pid}/root/var/etcd/ssl/client/ca/bundle.crt \\
  --cert=proc/${wrapper_pid}/root/var/etcd/ssl/client/client/tls.crt \\
  --key=proc/${wrapper_pid}/root/var/etcd/ssl/client/client/tls.key \\
  --endpoints=https://etcd-main-local:2379

EOF