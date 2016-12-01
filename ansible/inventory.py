#!/usr/bin/env python

import argparse
import boto.ec2
import boto.elasticache
import json
import os
import pprint
import yaml

abspath = os.path.abspath(__file__)
dirname = os.path.dirname(abspath)
os.chdir(dirname)

f = open("group_vars/all/main.yml", "r")
default = yaml.load(f)
f.close()
region = default["aws_region"]
keypair = default["keypair"]
bench_tag = default["bench_tag"]

parser = argparse.ArgumentParser()
parser.add_argument("--hosts", help="List the hosts for the specified group")
parser.add_argument("--list", help="List the whole inventory", action="store_true")
args = parser.parse_args()

ec2 = boto.ec2.connect_to_region(region)

elasticache = boto.elasticache.connect_to_region(region)
clusterInfo = elasticache.describe_cache_clusters(show_cache_node_info=True)

redisHost = clusterInfo['DescribeCacheClustersResponse']['DescribeCacheClustersResult']['CacheClusters'][0]['CacheNodes'][0]['Endpoint']['Address']

reservations = ec2.get_all_instances(filters={"tag-key": "Role", "instance-state-name":"running", "tag:bench": bench_tag})
instances = [i for r in reservations for i in r.instances]

nuxeoreservations = ec2.get_all_instances(filters={"tag:Role": "nuxeo", "instance-state-name":"running", "tag:bench": bench_tag})
nuxeoinstances = [i for r in nuxeoreservations for i in r.instances]


esreservations = ec2.get_all_instances(filters={"tag:Role": "es", "instance-state-name":"running", "tag:bench": bench_tag})
esinstances = [i for r in esreservations for i in r.instances]

mongodbreservations = ec2.get_all_instances(filters={"tag:Role": "mongo", "instance-state-name":"running", "tag:bench": bench_tag})
mongodbinstances = [i for r in mongodbreservations for i in r.instances]


hostvars = {}
groups = {}

allinstances = []
allids = []
for i in instances + nuxeoinstances + mongodbinstances + esinstances:
    if i.id not in allids:
        allinstances.append(i)
        allids.append(i.id)

groups["aws"]={"hosts": []}

for i in allinstances:
    #pprint.pprint (i.__dict__)
    state = i._state.name
    if state != "running":
        continue
    role = i.tags["Role"]
    address = i.ip_address
    if role not in groups:
        groups[role] = {"hosts": []}
    groups[role]["hosts"].append(address)
    groups["aws"]["hosts"].append(address)

    hvars = {}
    hvars["id"] = i.id
    hvars["state"] = state
    hvars["image_id"] = i.image_id
    hvars["public_ip"] = i.ip_address
    hvars["private_ip"] = i.private_ip_address
    hvars["ansible_ssh_user"] = "ubuntu"

    hostvars[address] = hvars


inventory = {"_meta": {"hostvars": hostvars}}
inventory.update(groups)

if "nuxeo" not in inventory:
    inventory["nuxeo"] = {}
if "es" not in inventory:
    inventory["es"] = {}

inventory["nuxeo"]["vars"] = {"db_hosts": [], "es_hosts": [], "mongodb_hosts": [], "mgmt_hosts": [], "redis_hosts": [redisHost]}
inventory["es"]["vars"] = {"mgmt_hosts": []}
inventory["mongo"]["vars"] = {"mgmt_hosts": []}
inventory["management"]["vars"] = {"mgmt_hosts": [], "redis_hosts": [redisHost]}

if "db" in groups:
    for i in groups["db"]["hosts"]:
        inventory["nuxeo"]["vars"]["db_hosts"].append(hostvars[i]["private_ip"])
if "es" in groups:
    for i in groups["es"]["hosts"]:
        inventory["nuxeo"]["vars"]["es_hosts"].append(hostvars[i]["private_ip"])
if "mongo" in groups:
    for i in groups["mongo"]["hosts"]:
        inventory["nuxeo"]["vars"]["mongodb_hosts"].append(hostvars[i]["private_ip"])
if "management" in groups:
    for i in groups["management"]["hosts"]:
        inventory["nuxeo"]["vars"]["mgmt_hosts"].append(hostvars[i]["private_ip"])
        inventory["es"]["vars"]["mgmt_hosts"].append(hostvars[i]["private_ip"])
        inventory["mongo"]["vars"]["mgmt_hosts"].append(hostvars[i]["private_ip"])
        inventory["management"]["vars"]["mgmt_hosts"].append(hostvars[i]["private_ip"])

#print inventory

if args.hosts:
    print " ".join(inventory[args.hosts]["hosts"])
else:
    print json.dumps(inventory, sort_keys=True, indent=2)

