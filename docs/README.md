    UDM5G-EST Provisioning

## History
- 29/06/2018 - emaante - Added short how-to guide on basic    configuration and execution
- 20/07/2018 - emaante - Updated, following project-level changes
- 26/10/2018 - emaante - Minor updates
- 18/12/2018 - epremio - Updated this readme file and made a couple of changes with the new PXE server. Upgraded version of default software installation. 

# Project composition
- docs/
Documentation dir, this README is stored there

- library/
Custom Ansible modules

- roles/
VMware CRUD functionality splitted into logical tasks +
Various fixes and workarounds

- var/
Stores various configuration files necessary for playbook execution

- xml/
Stores XMLs used in REST API calls, !DO NOT EDIT!

- vmware_provisioning.yml
Main playbook, for VM provisioning

- eccd_fixes.yml
Various fixes for ECCD clusters (kubelet, docker etc.)

- node_exporter.yml
Provisioning of node exporter daemon for Prometheus/Grafana monitoring


# HOW TO EXECUTE
# If this is your first time cloning the repo, you need to create the ansible vault file in ./var/
*cd var*
*ansible-vault create secret.yml*

- provide password for your vault when prompted (to protect it)
- if you forget it, you will have to create new vault file
- eache edit of vault file prompts for new vault password (security measure)

*./var/secret.yml.example:*

api_host_vmware: "https://vcloud.seli.gic.ericsson.se"
api_host_hydra: "https://hydra.gic.ericsson.se"
api_host_pxe: "http://api.lxgen.seli.gic.ericsson.se"
api_user: "<your /// signum>"
api_password: "<your ecn password>"
api_token_hydra: "<hydra static_token>"

- *api_host_** variables should be used as provided
(they were put as configurations option should lab config change)

- *api_token_hydra* can be obtained from: https://hydra.gic.ericsson.se/user


# Specify vApp configuration data:
- We need to copy the ./var/shared_vdc_vars.template ti ./var/shared_vdc_vars.yml and modify settings
*cp ./var/shared_vdc_vars.templar ./var/shared_vdc_vars.yml*
# edit and customize the file (replace <signum> and <JIRA_ID> variables)
*vim ./var/shared_vdc_vars.yml*
- you are supposed to change vApp configurations details ('_name', '_tmpl_name', '_decription', 'vm_count')
  and 'os_profile'
- it is recommended to keep 'tmp_xml' dir location inside your home dir
- 'org_network_name' is fixed and should not be changed
- likewise, 'hydra_tmpl_name' is fixed and should not be changed

#local dir to save HTTP actions   
tmp_dir: "/home/<your signum here>/tmp_xml"

#Hydra template to create CI entry   
hydra_tmpl_name: "udm_5gEST_ci_template"

#vApp configuration details   
#vapp_tmpl_name: "udm_test"  
vapp_tmpl_name: "udm_eccd_rhel"
vapp_name: "<signum>_devenv_<JIRA ID>"   
vapp_description: "UDM-5G shared vApp <signum>"  
vm_count: 1   
# org_network_name: "137-UDM 5G management E2C POD2"
org_network_name: "339-UDM 5G mgmt E2C POD3 second"

#VM configurations details   
os_profile: "ubuntu"


# Specify VDC configuration details
*./var/vmware_shared_vdc.yml*

#vCloud connection data for Shared VDC   
org_name: "shared"  
vdc_name: "shared-e2c-seli-pod3-vdc"   
catalog_name: "udmvm_template"

- there are 2 VDC configuration files:
  vmware_shared_vdc.yml
  vmware_udm_vdc.yml

- choose one to specify in which VDC to deploy vApp
- values in those files are basically constants,
  you do not have to edit anything

# Run playbook

## Create provisioning

#### on UDM vDC
ansible-playbook -vvv -i localhost -c ssh -e@./var/secret.yml -e@./var/udm_vdc_vars.yml -e@./var/vmware_udm_vdc.yml vmware_provisioning.yml --ask-vault-pass --tags "create"

#### on Shared vDC
ansible-playbook -vvv -i localhost -c ssh -e@./var/secret.yml -e@./var/shared_vdc_vars.yml -e@./var/vmware_shared_vdc.yml vmware_provisioning.yml --ask-vault-pass --tags "create"

- when asked for password, provide it to unlock secret.yml vault file (and decrypt username/password/api endpoints etc.)
- wait for playbook to run its course
- vApp with 1 VM is deployed in 4:30m, with 8 VMs in 30:15m; OS installation & Puppet configuration completed in +16min after last VM is deployed
- if vApp does not exist, playbook creates one, with specified number of VMs
- if vApp exists, but has less than specified number of VMs, playbook adds more VMs to it, up to specified count
- otherwise, vApp is left as it is

## Delete provisioning
#### Also choose either UDM or Shared vDC
ansible-playbook -vvv -i localhost -c ssh -e@./var/secret.yml -e@./var/shared_vdc_vars.yml -e@./var/vmware_shared_vdc.yml vmware_provisioning.yml --ask-vault-pass --tags "delete"

- every trace is cleaned: CI entries in Hydra, PXE configurations and finally, vApp itself
- vApp with 1 VM is completely cleaned in 0:45min, with 8 VMs in 2:00m

## Retrieve provisioning
ansible-playbook -vvv -i localhost -c ssh -e@./var/secret.yml -e@./var/shared_vdc_vars.yml -e@./var/vmware_shared_vdc.yml vmware_provisioning.yml --ask-vault-pass --tags "retrieve"

- quickly builds inventory file {tmp_dir}/{vapp_name}_inventory_file, as specified from vars in /var/shared_vdc_vars.yml

