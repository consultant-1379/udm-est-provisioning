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
module: e3utils_rosetta_user

short_description: Ansible module to interact with Rosetta users. 

version_added: "0.1"

description:
    - "This module allows the query of Rosetta users. The module returns a list of the groups that the user is a member of when the user exists, and fails when the user is not found in Rosetta."

options:
    user:
        description:
            - Name of the Rosetta user (signum) to be queried.
        required: true
        type: string

requirements:
    - "E3tools must be correctly installed and configured in the host where the module is executed. (https://confluence.lmera.ericsson.se/display/GLPUT/UDM+E3+tools+-+Preparation+of+environments+for+E3Tools+usage)"

authors:
    - zaraualm
    - zdavvil
'''

EXAMPLES = '''

'''

RETURN = '''

'''
def main():  

  global module
  global rosetta

  module_args = dict(
    user = dict(required=True, type='str'),
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
  user_info = rosetta.get(module.params['user'], 'AppUser')
  user_groups = list ()

  if not user_info:
      msg = "The user does not exist in Rosetta."
      has_failed = True
      has_changed = False
      result = {}

  else:
      
      user_groups_query = rosetta.custom_query("teams/?users=" + str(user_info.id))
      
      for group in user_groups_query:
        user_groups.append (group['name'])

      msg = "The user exists in Rosetta."
      has_failed = False
      has_changed = False
      result = { "count":  len(user_groups), "groups": user_groups }

  module.exit_json(msg=msg , failed= has_failed, changed=has_changed, result=result)

if __name__ == '__main__':  # pragma: no cover
    main()