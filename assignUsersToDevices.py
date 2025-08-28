import csv
import os
import requests
import sys

# Configuration
BASEURL=os.getenv("JAMF_BASE_URL")
print(f"BASEURL: {BASEURL}")
API_TOKEN=os.getenv("JAMF_API_TOKEN")
print(f"API_TOKEN: {API_TOKEN}")

SERIAL_TO_UDID_API_URL = f"{BASEURL}/devices/"
SET_USER_API_URL = f"{BASEURL}/devices/" # Add UDID + '/owner' to the end of this
GET_USERS_API_URL = f"{BASEURL}/users/"
GET_GROUPS_API_URL = f"{BASEURL}/devices/groups"
API_HEADERS = {
    "Authorization": f"Basic {API_TOKEN}",
    "Content-Type": "application/json"
}
DEFAULT_CSV_FILE = "jamfscriptinput.csv"  # Your input file


ADD_TO_GROUP_API_URL = f"{BASEURL}/devices/groups/add"

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
        
def get_users():
    response = requests.get(f"{GET_USERS_API_URL}", headers=API_HEADERS)
    if response.status_code == 200:
        data = response.json()
        userCount = data["count"]
        users = data["users"]
        return users
    else:
        print(f"Failed to get users: {response.status_code}")
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

def read_data_from_csv(filepath):
    """Read serial numbers from a CSV file with a column 'serial_number'."""
    serials = []
    """Read names from a column 'last_first'."""
    names = []
    """Read groups from a column 'group'."""
    groups = []


    with open(filepath, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            serial = row.get("serial_number")
            if serial:
                serials.append(serial.strip())

            name = row.get("last_first")
            names.append(name)

            group = row.get("group")
            groups.append(group)
    return serials, names, groups

def make_lastFirst_into_firstLast(name):
    last, first = name.split(",")
    new_name = f"{first.strip()} {last.strip()}"
    return new_name

def get_userId_by_username(name, users):
    for user in users:
        if user["username"] == name:
            return(user["id"])
        
    return None

def get_groupId_by_name(groupName, groups):
    for group in groups:
        if group["name"] == groupName:
            return(group["id"])
        
    return None

# Creates a user in JAMF
#.   param: name in Last, First form, like "Smith, John"
#.   return: id of created user. If unable to create, returns None
def create_user(name):
    last, first = last, first = name.split(",")
    new_name = f"{first.strip()} {last.strip()}"
    payload = {
        "username": new_name,
        "password": "",
        "email": "",
        "firstName": first,
        "lastName": last
    }
    response = requests.post(f"{GET_USERS_API_URL}", json=payload, headers=API_HEADERS)
    if response.status_code == 200:
        responseData = response.json()
        id = responseData["id"]
        print(f"Created user {id}")
        return id
    else:
        print("Failed to create user")
        print(response.text)
        return None

# Creates a group in JAMF
#.   param: name of the group
#.   return: id of created group. If unable to create, returns None
def create_group(name):
    payload = {
        "name": name
    }
    response = requests.post(f"{GET_GROUPS_API_URL}", json=payload, headers=API_HEADERS)
    if response.status_code == 200:
        responseData = response.json()
        id = responseData["id"]
        print(f"Created group {id}")
        return id
    else:
        print("Failed to create group")
        print(response.text)
        return None

def assign_user_to_device_by_udid(userID, udid):
    payload = {
        "user": userID
    }
    response = requests.put(f"{SET_USER_API_URL}{udid}/owner", json=payload, headers=API_HEADERS)
    if response.status_code == 200:
        print(f"Assigned user {userID} to UDID {udid}")
        return True
    else:
        print(f"Failed to assign user {userID} to UDID {udid}")
        print(response.text)
        return False

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

def main():
    users = get_users()
    groupsInJamf = get_groups()

    # If a filename is given on the command line, use it; otherwise use default
    csv_file = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CSV_FILE
    

    serial_numbers, names, groups = read_data_from_csv(csv_file)
    for serial, name, groupName in zip(serial_numbers, names, groups):
        lastFirst = name
        print(f"lastFirst: {lastFirst}")
        firstLast = make_lastFirst_into_firstLast(lastFirst)
        userId = get_userId_by_username(firstLast, users)
        if not userId:
            userId = create_user(lastFirst)
            users = get_users()

        groupId = get_groupId_by_name(groupName, groupsInJamf)
        if not groupId:
            groupId = create_group(groupName)
            groupsInJamf = get_groups()
        
        udid = get_udid_from_serial(serial)
        userAssigned = assign_user_to_device_by_udid(userId, udid)
        if userAssigned:
            print(firstLast, serial, userId)
        else:
            print(f"************* ERROR FOR {firstLast} {serial} {userId}")

        groupAssigned = assign_device_to_group_by_udid(groupId, udid)
        if groupAssigned:
            print(f"{serial} assigned to group {groupId}")
        else:
            print(f"************* ERROR FOR {serial} {groupId}")

if __name__ == "__main__":
    main()
