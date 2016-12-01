# NST4A

 Nuxeo Stack Tuned for AWS 

 Yet another ansible script repo to provision a Nuxeo stack on AWS


## Target infrastructure

The test profile will provision and setup the following stack:

- mongodb: m4.2xlarge (8cpu, 30g ram, 100g SSD)
- elasticsearch: m4.2xlarge (8cpu 30g ram, 200g SSD)
- nuxeo: c4.2xlarge (8cpu, 15g ram, 120g)
- redis: cache.m3.xlarge

- monitoring: c4.xlarge (4cpu, 7g, 30g SSD)

Cost: ~$2.10/h

## Requirements


### Clone the scripts

    git clone <>

### Ansible requirement


    cd /path/to/nst4a
    
    virtualenv venv
    . venv/bin/activate
    pip install -q -r ansible/ansible-requirements.txt

    # install ansible plugin require write to /etc/ansible
    sudo chown $USER.$USER -R /etc/ansible
    ansible-galaxy install --force -r requirements.txt
    sudo chown root.root -R /etc/ansible
    popd

### Configure AWS environment

    # edit the ansible/group_vars/all/main.yml to set your keypair, aws region and project name

    # setup a valid AWS access in ~/.aws/credentials used by inventory ec2 boto
    # this may requires to generate Security Credential from aws console IAM/Users/(keypair)/Security Credential/Create access Key

    # activate the virtual env before running ansible script:
    . venv/bin/activate
    export ANSIBLE_HOST_KEY_CHECKING=False


## Create the Nuxeo stack

### Provisioning using cloudformation

    pushd ./ansible
    ansible-playbook -vv  provision.yml

### Configure the stack

    pushd ./ansible
    ansible-playbook -vv  -i inventory.py  site.yml

### Inventory of the stack

    python ./ansible/inventory.py

## Accessing

Get the ip from the inventory (see section above).

Nuxeo: http://<nuxeo-ip>:8080/nuxeo
Monitoring Grafana: http://<monitoring-ip>/
Monitoring Graphite: http://<monitoring-ip>:8080/

## Actions
 
### Start/Stop Nuxeo

### Reset data
 
### Run the importer

ssh to the nuxeo instance then run it manually. 

## TODO

- impl the prod profile with a Nuxeo cluster
- Use the nuxeo-importer-queue importer