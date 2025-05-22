# JAMF-scripts

Scripts to perform various tasks for JAMF School, and the template for a CSV file that works with the scripts.

| Script | Description | Required CSV Field(s) |
| --- | --- | :---: |
| removeUsersFromDevices.py | Reads a list of serial numbers from csv and removes the users in JAMF | serial_number |

## Configuration

  Set environment variables JAMF_BASE_URL and JAMF_API_TOKEN
```
      export JAMF_BASE_URL="https://{yourdomain}.jamfcloud.com/api"
      export JAMF_API_TOKEN="{your token}"
```
Instructions for generating your API Token can be found [here](https://hudsoncs.jamfcloud.com/api/docs/). You'll need the Network ID from **Devices > Enroll Device(s)**. I used [this site](https://scf37.me/tools/base64-decoder) to get the MIME encoded string.
