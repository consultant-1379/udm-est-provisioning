#!/usr/bin/python
"""E3utils rosetta ansible module"""
from ansible.module_utils.basic import *

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'e3utils,est_5g'
}

DOCUMENTATION = '''
---
module: e3utils_rosetta_tool

short_description: Ansible module to interact with Rosetta Tools.

version_added: "0.2"

description:
    - "This module allows the creation, modification and deletion of Rosetta Tool nodes."

options:
    name:
        description:
            - Name of the Rosetta Tool to be managed.
        required: true
        type: string

    infratype:
        description:
            - Infra type of the Rosetta Tool to be managed.
        required: true
        type: string

    ndo:
        description:
            - NDO of the Rosetta Tool to be managed.
        required: true
        type: string

    team:
        description:
            - Team of the Rosetta Tool to be managed.
        required: true
        type: string

    team_admin:
        description:
            - Administration Team of the Rosetta Tool to be managed.
        required: true
        type: string

    owner:
        description:
            - Signum of the owner of VM to be managed as a Tool in Rosetta. The owner's signum must be registered in Rosetta before the Tool is created. This signum must be a member of the Rosetta team provided in the 'team' parameter of the module.
        required: true
        type: string

    status:
        description:
            - Status of the Rosetta Tool to be managed.
        choices: [ busy ]
        default: busy

    hydra_synced:
        description:
            - Determines if the Rosetta Tool is synchronized with Hydra.
        default: true
        type: bool

    automanaged:
        description:
            - Deterines if the Rosetta Tool is automanaged.
        default: true
        type: bool

    additional_info:
        description:
            - List of key/value variables to be registered in Rosetta apart from the Tool data model. These parameters allow extending the data model of Rosetta without its refactor.
        type: dict

    state:
        description:
            - Desired status of the Rosetta Tool to be managed.
        required: true
        choices: [ absent, present ]
        default: present
        type: string

    create:
        description:
            - If create is enabled, for any mode, the module will create a new Tool if it didn't exist before in Rosetta.
        default: False
        type: bool

    mode:
        description:
            - Applies when the status is set to 'present'. Defines the mode in which the Ansile will interact with the Rosetta Tool will be managed.
            - If 'exact' mode is selected, the module will fail if the Tool did exist with different settings than the ones provided to the module.
            - If 'overwrite' mode is selected, the module will overwrite the Tool with the new parameters if any of the existing settings were different from the ones provided to the module.
            - If 'append' mode is selected, the new settings will be appended (additional_info) to the new settings if any of the existing was different from the ones provided to the module. No elements in the existing additional_info parameter will be deleted in an existing Rosetta object.
        choices: [ exact, overwrite, append ]
        default: exact
        type: string

requirements:
    - "E3tools must be correctly installed and configured in the host where the module is executed. (https://confluence.lmera.ericsson.se/display/GLPUT/UDM+E3+tools+-+Preparation+of+environments+for+E3Tools+usage)"

KNOWN ISSUES:

    - When the value of a key/value pair stored in the additional_info is set to 'none', the modes overwrite and exact have some errors.
    - When a void user is provided, the module crashes because Rosetta provides all the users when asked for a null user.
    - The Rosetta additional_info has some info generated automatically generated that should be moved to a different field.

authors:
    - xcriper
    - zdavvil
'''

EXAMPLES = '''

  - name: Verify if Tool exist in  Rosetta.
    local_action:
      module:     e3utils_rosetta_tool
      name:       seliius99999
      ndo:        5G_EST
      team:       5G_BSP
      team_admin: 5G_Program
      owner:      zdavvil
      state:      present

  - name: Obtain the info of the Tool if it exist in  Rosetta.
    local_action:
      module:     e3utils_rosetta_tool
      name:       seliius99999
      ndo:        5G_EST
      team:       5G_BSP
      team_admin: 5G_Program
      owner:      zdavvil
      state:      present

  - name: Verify if Tool exist with exact parameters in  Rosetta.
      module:     e3utils_rosetta_tool
      name:       seliius99999
      infratype:  5g_dev_vm_small
      ndo:        5G_EST
      team:       5G_BSP
      team_admin: 5G_Program
      owner:      zdavvil
      state:      present
      mode:       exact
      additional_info:
        - sudoers:        zdavvil
        - provider:       vdc_shared

  - name: Modify a Tool in Rosetta.
    local_action:
      module:     e3utils_rosetta_tool
      name:       seliius99999
      infratype:  5g_dev_vm_small
      ndo:        5G_EST
      team:       5G_BSP
      team_admin: 5G_Program
      owner:      zdavvil
      state:      present
      create:     true
      mode:       overwrite
      additional_info:
        - sudoers:        zdavvil
        - provider:       vdc_shared
        - tenant:         shared
        - jira:           JIRA-999
        - revision:       V3
        - ipv6_support:   false
        - HydraSyncSTatus: "The syncronization with hydra is updated"
    
  - name: Delete Tool in Rosetta.
    local_action:
      module:     e3utils_rosetta_tool
      name:       seliius99999
      state:      absent

'''

RETURN = '''

'''

def present (tool_params, create, mode):

# The aim of this function is to manage the verification/creation of Tool objects in Rosetta.

#   - When create is True, the module will create a new tool if it didn't exist in Rosetta.
#   - When create is False, the module will return an error if the Tool didn't exist in Rosetta.

# If the Tool did exist in Rosetta, then the function will manage it according to the mode selected:

#   - exact:      this mode will verify if every attribute of the Tool matches with the parameters provided to the module. If it didn't the module will return an error.
#   - overwrite:  this mode will overwrite the Tool with the settings provided by the module. This can, in turn, delete some of the settings registered in Rosetta previously, especially those registered in the additional_info field.
#   - overwrite:  this mode will rewrite the Tool with the settings provided by the module, but only adding information to the Tool, not deleting any preexisting info, especially those registered in the additional_info field.

  try:
      import e3utils.e3types
  except ImportError as err:
        module.exit_json (failed="True", changed="False", meta=err)

  # Create an e3utils object with the data provided to the module.

  new_tool = e3utils.e3types.new (tool_params)

  # Load an e3type with the data stored in Rosetta. If no object is registered with the name provided to the module, the e3type
  # will be  set to null.

  previous_tool = rosetta.get (tool_params['name'], "Tool")
  items_to_compare = tool_params.keys()

  has_changed = False
  meta = {}

  # If the object was NOT PRESENT in Rosetta: create a new one when 'create' flag is enabled,
  # or return a failed code when the flag 'create' is disabled.

  if not previous_tool:
    
    if create:
        has_changed = True
        meta = rosetta.save(new_tool).as_dict
        return (has_changed, meta)

    if not create:
        module.fail_json(msg="The tool node has not been found in Rosetta.")

  # If the object was PRESENT in Rosetta: operate according to the value of the flag 'mode'.

  equal = new_tool.compare_list(previous_tool, items_to_compare)


  if mode == 'exact':

    if equal:    
        has_changed = False
        meta = previous_tool.as_dict
        return (has_changed, meta)
    else:
        module.fail_json(msg="The tool node is not exactly as the provided one.", meta = previous_tool.additional_info)
      
  if mode == 'overwrite':

    if not equal:
        for attr in items_to_compare:
            if attr == 'classtype':
              continue
            setattr (previous_tool, attr, getattr (new_tool, attr))
        has_changed = True
        meta = rosetta.update(previous_tool).as_dict
        return (has_changed, meta)

  if mode == 'append':

    if not equal:
        for attr in items_to_compare:
            if attr == 'classtype':
              continue
            if attr == 'additional_info':
              previous_tool.additional_info.update (new_tool.additional_info)
              continue

            setattr (previous_tool, attr, getattr (new_tool, attr))

        has_changed = True
        meta = rosetta.update(previous_tool).as_dict
        return (has_changed, meta)

  # If no mode flag is specified, the module returns the value of the tool as registered in Rosetta.

  has_changed = False
  meta = previous_tool.as_dict
  return (has_changed, meta)

def absent (tool_params):

# The aim of this function is delete a Tool object in Rosetta if it did exist before.

  try:
      import e3utils.e3types
  except ImportError as err:  # pragma: no cover
        module.exit_json (failed="True", changed="False", meta=err)

  tool = e3utils.e3types.new (tool_params)

  previous_tool = rosetta.get (tool_params['name'], "Tool")

  # The object is looked up in Rosetta, and if it is found, its reletion is requested.

  if not previous_tool:
    has_changed = False  
    meta = {}
  else:
    has_changed = True
    meta = previous_tool.as_dict
    rosetta.delete(tool)
  
  return (has_changed, meta)


def main():  

  global module
  global rosetta

  module_args = dict(
    name            = dict(required=True, type='str'),
    infratype       = dict(required=True, type='str'),
    ndo             = dict(required=True, type='str'),
    team            = dict(required=True, type='str'),
    team_admin      = dict(required=True, type='str'),
    owner           = dict(default=None, type='str'),
    status          = dict(default='busy', choices=['busy', 'free']),
    hydra_synced    = dict(default=True, type='bool'),
    automanaged     = dict(default=True, type='bool'),
    additional_info = dict(required=False, type='list'),
    state           = dict(default='present', choices=['present', 'absent']),
    create          = dict(default=False, type='bool'),
    mode            = dict(choices=['exact', 'append', 'overwrite'], type='str'),
  )
  
  module = AnsibleModule(argument_spec=module_args)

  try:
      import os.path
  except:
      module.fail_json(msg="Cannot import os.path module.")

  try:
      from e3utils.clients.rosetta import Rosetta
  except:
      module.fail_json(msg="Cannot import Rosetta.Please, verify the e3utils installation.")

  try:
      assert  os.path.exists (os.path.expanduser('~') + '/.e3config')
  except:
      module.fail_json(msg="Cannot find e3utils config file. Please, verify the e3utils condiguration.")

  rosetta = Rosetta()
  
  additional_info = {} 

  # The additional info data is provided by Ansible as a list of dictionaries to the module. It is requred to transform it to a
  # dictionary before loading it into the e3type.

  for key_value in module.params['additional_info']:
      for key in key_value:
          additional_info.update({key : key_value [key]})

  try:
    tool_e3type_params = {
        "classtype": "Tool",
        "name": module.params['name'],
        "infratype": rosetta.get (module.params['infratype'],"InfraType"),
        "ndo": rosetta.get (module.params['ndo'], "NDO"),
        "team": rosetta.get (module.params['team'], "Team"),
        "team_node_administrator": rosetta.get (module.params['team_admin'], "Team"),
        "owner": rosetta.get (module.params['owner'], "AppUser"),
        "status": rosetta.get (module.params['status'], "Status"),
        "hydra_synced": module.params['hydra_synced'],
        "automanaged": module.params['automanaged'],
        "additional_info": additional_info
    }

  except:
      module.fail_json(msg="Error when generating a Rosetta Tool object. Please, check the parameters", meta=tool_e3type_params.as_dict)

  create = module.params['create']
  mode = module.params['mode']
  
  
  if module.params['state'] == 'present':   
      has_changed, result = present (tool_e3type_params, create, mode)

  if module.params['state'] == 'absent':
      has_changed, result = absent (tool_e3type_params)
  
  module.exit_json(changed=has_changed, result=result)

if __name__ == '__main__':  # pragma: no cover
    main()