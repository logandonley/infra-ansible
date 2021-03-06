#!/usr/bin/python3

DOCUMENTATION = '''  
---
module: fetch-data-gsheets
short_description: Grab users and user_groups info from google sheet and return it as a json string.
'''

EXAMPLES = '''  
- name: Pull data from google sheet & store it as users and user_groups facts.
  fetch-data-gsheets:
    spreadsheet_url: 'https://docs.google.com/spreadsheets/d/xxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    worksheet_name: 'Sheet1'
    credentials_src: '/path/to/instance/credentials.json'
    state: 'present'l
  register: result
'''

from ansible.module_utils.basic import *
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import datetime


# Function to extract the values from the google spreadsheet
# and outputs it as a json file.
def list_all(spreadsheet_url, worksheet_name, cred_file):
    wks = open_sheet(spreadsheet_url, worksheet_name, cred_file)
    vals = wks.get_all_values()
    headers = []
    for header in vals[0]:
        headers.append(header)
    del vals[0]
    json_list = []
    for row in vals:
        row_data = dict(zip(headers, row))
        json_list.append(dict((k, v) for k, v in row_data.items() if v))
    return json_list


# Grabs the credentials for Google sheets from an inputted credentials file.
def get_credentials(cred_file):
    scope = ['https://spreadsheets.google.com/feeds']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(cred_file, scope)
    return gspread.authorize(credentials)


# Takes the outputted json from the list_all function and returns it as the expected
# Ansible format.
def return_json(data):
    json_list = list_all(data['spreadsheet_url'], data['worksheet_name'], data['credentials_src'])
    has_changed = False
    meta = {"status": "Pulled data", "json": json_list}
    return has_changed, meta


# Returns the specified worksheet.
def open_sheet(spreadsheet, worksheet, cred_file):
    gc = get_credentials(cred_file)
    wks = gc.open_by_url(spreadsheet).worksheet(worksheet)
    return wks


# Main Ansible module definition
def run_module():
    fields = {
        "spreadsheet_url": {"required": True, "type": "str"},
        "worksheet_name": {"required": True, "type": "str"},
        "credentials_src": {"required": True, "type": "str"},
        "state": {
            "default": "present",
            "choices": ['present'],
            "type": "str"
        }
    }
    choice_map = {
        "present": return_json,
    }
    module = AnsibleModule(argument_spec=fields)
    has_changed, result = choice_map.get(module.params['state'])(module.params)
    module.exit_json(changed=has_changed, meta=result)


def main():
    run_module()


if __name__ == '__main__':
    main()
