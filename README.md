# JAMF-scripts

Scripts to perform various tasks for JAMF School, and the template for a CSV file that works with the scripts.

| Script | Description | Required CSV Field(s) |
| --- | --- | :---: |
| assignUsersToDevices.py | Reads a list of serial numbers, device owner names (in "Lastname, Firstname" format), and device group names from csv. Assigns the owner to the device (creating a user if needed), and places the device in the group (creating the group if needed). Usernames will be in "Firstname Lastname" format. | serial_number, last_first, group |
| clearPasscodes.py | **OBSOLETE - REPLACED BY getDevicesWithPasscodes.py** | - |
| createClasses.py | Reads a list of device group names from csv and device owner names (in "Lastname, Firstname" format) and places users in a new class. It is assumed that the teacher will be listed first, followed by students in the teacher's class. Teachers must have the group "Staff iPads". Multiple teachers can be added - the role listed in the CSV must be "teacher" or "student". | group, last_first, role |
| emptyGroups.py | **WIP: Not functional yet** This will read a CSV of group names, and remove all devices from those groups (intended to prepare the groups for filling with assignUsersToDevices.py) | device_group |
| getDevicesWithPasscodes.py | Retrieves all devices in JAMF and prints out serial numbers of those with passcodes. | - |
| removeDevicesFromGroups.py | Reads a list of serial numbers and groups from csv and removes the devices from the specified group. **THIS SCRIPT DOES NOT WORK IN ITS CURRENT FORM** | serial_number, group |
| removeUsersFromDevices.py | Reads a list of serial numbers from csv and removes the users in JAMF | serial_number |
| removeWhitespaceFromUsers.py | Retrieves all users in JAMF. If any users have leading or trailing whitespace in the Firstname, Lastname, or Username fields, removes it and updates the user in JAMF | - |
| wipeDevices.py | Reads a list of serial numbers from csv and sends the command to wipe the device | serial_number |

## Configuration

  Set environment variables JAMF_BASE_URL and JAMF_API_TOKEN
```
      export JAMF_BASE_URL="https://{yourdomain}.jamfcloud.com/api"
      export JAMF_API_TOKEN="{your token}"
```
Instructions for generating your API Token can be found [here](https://hudsoncs.jamfcloud.com/api/docs/). You'll need the Network ID from **Devices > Enroll Device(s)**. I used [this site](https://scf37.me/tools/base64-decoder) to get the MIME encoded string.

The **jamfscriptinput.csv** file must be in the same directory as the script being run.
