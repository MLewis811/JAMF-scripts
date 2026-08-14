import csv
import os
import requests
import sys

# Configuration
BASEURL=os.getenv("JAMF_BASE_URL")
print(f"BASEURL: {BASEURL}")
API_TOKEN=os.getenv("JAMF_API_TOKEN")
print(f"API_TOKEN: {API_TOKEN}")
API_HEADERS = {
    "Authorization": f"Basic {API_TOKEN}",
    "Content-Type": "application/json"
}

SERIAL_TO_UDID_API_URL = f"{BASEURL}/devices/"
GET_DEVICES_API_URL = f"{BASEURL}/devices/"
GET_GROUPS_API_URL = f"{BASEURL}/devices/groups"
ADD_TO_GROUP_API_URL = f"{BASEURL}/devices/groups/add"
REMOVE_DEVICE_FROM_GROUP_API_URL = f"{BASEURL}/devices/groups/remove"

def get_devices():
    response = requests.get(f"{GET_DEVICES_API_URL}", headers=API_HEADERS)
    if response.status_code == 200:
        data = response.json()
        devices = data["devices"]
        return devices
    else:
        print(f"Failed to get devices: {response.status_code}")
        return None

def get_serial_number_by_user(username, devices):
    for device in devices:
        if device["owner"].get("username") == username:
            return device["serialNumber"]
    
    return None

def get_udid_from_serial(serial):
    """Fetch UDID from serial number using the API."""
    response = requests.get(f"{SERIAL_TO_UDID_API_URL}?serialnumber={serial}", headers=API_HEADERS)
    # print(f"SN {serial}: status {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        devCount = data["count"]
        if devCount == 1 :
            udid = data["devices"][0]["UDID"]
            print(f"SN {serial}: UDID {udid}")
            return udid
        else:
            print(f"{devCount} devices found for serial {serial}")
            return None
    else:
        print(f"Failed to get UDID for serial {serial}: {response.status_code}")
        return None

def get_groups():
    response = requests.get(f"{GET_GROUPS_API_URL}", headers=API_HEADERS)
    if response.status_code == 200:
        data = response.json()
        groups = data["deviceGroups"]
        return groups
    else:
        print(f"Failed to get groups: {response.status_code}")
        return None

def get_groupId_by_name(groupName, groups):
    print(f"Looking for group {groupName}")
    for group in groups:
        if group["name"] == groupName:
            print(f"Found {groupName}! ID = {group["id"]}")
            return(str(group["id"]))
        
    return None

def read_data_from_csv(filepath):
    """Read groups from a column 'device_group'."""
    groups = []


    with open(filepath, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            group = row.get("device_group")
            groups.append(group)
    return groups

def assign_device_to_group_by_udid(groupId, udid):
    payload = {
        "groupId": groupId,
        "udids": [udid]
    }
    response = requests.post(f"{ADD_TO_GROUP_API_URL}", json=payload, headers=API_HEADERS)
    if response.status_code == 200:
        print(f"Assigned udid {udid} to group {groupId}")
        return True
    else:
        print(f"Failed to assign udid {udid} to group {groupId}")
        print(payload)
        print(response.text)
        return False
    
def remove_devices_from_group_by_udid(udids, group_id):
    if not udids:
        print("No devices to remove!")
        return
    
    payload = {
        "groupId": group_id,
	    "udids" : udids
	} 
    response = requests.post(REMOVE_DEVICE_FROM_GROUP_API_URL, json=payload, headers=API_HEADERS)
    if response.status_code == 200:
        print("Successfully removed devices from the group.")
    else:
        print(f"Failed to remove devices to the group: {response.status_code}")
        print(response.text)
        

def main():
    devices = get_devices()
    groups = get_groups()

    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    else:
        print("Specify a CSV file")
        return
    
    groupsToEmpty = read_data_from_csv(csv_file)
    for groupName in groupsToEmpty:
        groupId = get_groupId_by_name(groupName, groups)
        # print(f"Devices with group ID {groupId}")
        devicesInGroup = [
            device["UDID"] for device in devices
            if groupId in device.get("groupIds", [])
        ]
        # print(devicesInGroup)

        remove_devices_from_group_by_udid(devicesInGroup, groupId)


if __name__ == "__main__":
    main()
