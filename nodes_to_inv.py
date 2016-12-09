#!/usr/bin/env python

# A simple dynamic replacemant of 'kargo prepare'
# Generates ansible inventory from a list of IPs in 'nodes' file.

import argparse
import json
import os
import yaml

def read_nodes_from_file(filename):
    f = open(filename, 'r')
    content = [x.strip('\n') for x in f.readlines()]
    return content

def read_vars_from_file(src="/root/kargo/inventory/group_vars/all.yml"):
    with open(src, 'r') as f:
        content = yaml.load(f)
    return content

def nodes_to_hash(nodes_list, masters, calico_rrs, group_vars):
    nodes = {
          'all': {
              'hosts': [],
              'vars': group_vars
          },
          'etcd': {
              'hosts': [],
          },
          'kube-master': {
              'hosts': [],
          },
          'kube-node': {
              'hosts': [],
          },
          'k8s-cluster': {
              'children': ['kube-node', 'kube-master']
          },
          'calico-rr': {
              'hosts': [],
          },
          '_meta': {
              'hostvars': {}
          }
    }
    i = 0

    for node_ip in nodes_list:
        i += 1
        node_name = "node%s" % i
        nodes['all']['hosts'].append(node_name)
        nodes['_meta']['hostvars'][node_name] = {
            'ansible_ssh_host': node_ip,
            'ip': node_ip,
        }

        if i <= calico_rrs:
#            cluster_id = "1.0.0.%s" % i
            cluster_id = "1.0.0.1"
            nodes['calico-rr']['hosts'].append(node_name)
            nodes['_meta']['hostvars'][node_name]['cluster_id'] = cluster_id
            continue

        nodes['kube-node']['hosts'].append(node_name)
        if i <= masters + calico_rrs:
            nodes['kube-master']['hosts'].append(node_name)
        if i <= 3 + calico_rrs:
            nodes['etcd']['hosts'].append(node_name)

    return nodes

def main():
    parser = argparse.ArgumentParser(description='Kargo inventory simulator')
    parser.add_argument('--list', action='store_true')
    parser.add_argument('--host', default=False)
    args = parser.parse_args()

    # Read params from ENV since ansible does not support passing args to dynamic inv scripts
    if os.environ.get('K8S_NODES_FILE'):
        nodes_file = os.environ['K8S_NODES_FILE']
    else:
        nodes_file = 'nodes'

    if os.environ.get('CALICO_RRS'):
        calico_rrs = int(os.environ['CALICO_RRS'])
    else:
        calico_rrs = 0

    if os.environ.get('K8S_MASTERS'):
        masters = int(os.environ['K8S_MASTERS'])
    else:
        masters = 2

    if os.environ.get('KARGO_GROUP_VARS'):
        vars_file = os.environ['KARGO_GROUP_VARS']
    else:
        vars_file = "/root/kargo/inventory/group_vars/all.yml"

    nodes_list = read_nodes_from_file(nodes_file)

    if len(nodes_list) < 3:
        print "Error: requires at least 3 nodes"
        return

    nodes = nodes_to_hash(nodes_list, masters, calico_rrs, read_vars_from_file(vars_file))

    if args.host:
        print json.dumps(nodes['_meta']['hostvars'][args.host])
    else:
        print json.dumps(nodes)

if __name__ == "__main__":
    main()
