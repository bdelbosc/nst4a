# NST4A

 Nuxeo Stack Tuned for AWS 

 Yet another ansible script repo to provision a Nuxeo stack on AWS


## Target infrastructure

The `test` profile will provision and setup the following stack of 5 instances:

- mongodb: m4.2xlarge (8cpu, 30g ram, 200g SSD)
- elasticsearch: m4.2xlarge (8cpu 30g ram, 200g SSD)
- nuxeo: c4.2xlarge (8cpu, 15g ram, 120g)
- redis: cache.m3.xlarge
- monitoring: c4.xlarge (4cpu, 7g, 30g SSD)

Cost: ~$2.10/h

## Requirements


### Clone the scripts

    git clone git@github.com:bdelbosc/nst4a.git
    cd ./nst4a

### Ansible requirement

1. Install the ansible requirement:
       
        virtualenv venv
        source venv/bin/activate
        pip install -q -r ansible/ansible-requirements.txt


2.  Install ansible plugin, this require a write access to `/etc/ansible` 

        sudo chown $USER.$USER -R /etc/ansible
        ansible-galaxy install --force -r requirements.txt
        sudo chown root.root -R /etc/ansible


### Configure AWS environment

1. Edit the `ansible/group_vars/all/main.yml` to set your `keypair`, the AWS region and project name aka `bench_tag`

2. Make sure your `awscli` is setup with a valid AWS access in your `~/.aws/credentials` this is used by the inventory (ec2 boto)
   you can generate a `Security Credential` from the AWS console: IAM/Users/(keypair)/Security Credential/Create access Key

3. Before running ansible command you need to activate the virtual environment:

        source venv/bin/activate
        export ANSIBLE_HOST_KEY_CHECKING=False


## Create the Nuxeo stack

### Provisioning with cloudformation


Run the playbook to create the needed instances:

    cd ./ansible
    ansible-playbook -vv  provision.yml
 
This can take few minutes. Once it is done you can list the inventory:

    python ./ansible/inventory.py


### Configure the stack

Here you need to have an ssh access to the instances, you may need to edit your `~/.ssh/config` to use your keypair like this:
  
    Host 54.*
       User ubuntu
       IdentityFile "/home/ben/.ssh/mykey-us-east-1.pem"


Once you have the ssh access you can run the ansible playbook to setup the stack:
  

    pushd ./ansible
    ansible-playbook -vv  -i inventory.py  site.yml


The Nuxeo is not yet started.


# Accessing

Get the public ip from the inventory (see section above).

- Nuxeo: http://nuxeo-ip:8080/nuxeo/
- Monitoring Grafana: http://monitoring-ip/
- Monitoring Graphite: http://monitoring-ip:8080/

# Actions
 
## Start/Stop Nuxeo

For now do it from nuxeo host:

    sudo service nuxeo start|stop

## Reset data
 
On Nuxeo:
 

    sudo service nuxeo stop
    echo "flushall" | redis-cli -h nyt-re-o81tzf435j2i.ocegtk.0001.euw1.cache.amazonaws.com
    curl -XDELETE elastic1:9200/nuxeo-audit;curl -XDELETE elastic1:9200/nuxeo;curl -XDELETE elastic1:9200/nuxeo-uidgen

On Mongo:

    service mongod stop && rm -rf /ssd1/mongodb/* && service mongod start
 
 
## Run the importer

From the nuxeo host:
 
    curl -XGET -vv -u Administrator:Administrator "http://127.0.0.1:8080/nuxeo/site/randomImporter/run?targetPath=/default-domain/workspaces&batchSize=30&nbThreads=20&interactive=false&nbNodes=1000000&fileSizeKB=0&bulkMode=true&onlyText=false&withProperties=true&blockAsyncProcessing=true&blockSyncPostCommitProcessing=true"


## Upload the Grafana dashboard

1. Log into the grafana UI (admin/admin)
2. Define a Data source named `graphite` that point to `http://graphite/`
3. Upload the dashboard `ansible/roles/management/files/nst4a-grafana.json` and use the ̀`grahite` data source.

# TODO

- provide more playbook: reset-data, restart nuxeo, import
- upload automatically the Grafana dashboard
- impl the prod profile with a Nuxeo cluster
- Use the nuxeo-importer-queue importer

# About Nuxeo

Nuxeo dramatically improves how content-based applications are built, managed and deployed, making customers more agile, innovative and successful. Nuxeo provides a next generation, enterprise ready platform for building traditional and cutting-edge content oriented applications. Combining a powerful application development environment with SaaS-based tools and a modular architecture, the Nuxeo Platform and Products provide clear business value to some of the most recognizable brands including Verizon, Electronic Arts, Netflix, Sharp, FICO, the U.S. Navy, and Boeing. Nuxeo is headquartered in New York and Paris. More information is available at www.nuxeo.com.
