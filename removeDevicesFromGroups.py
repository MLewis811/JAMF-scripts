import csv
import os
import requests

# Configuration
BASEURL=os.getenv("JAMF_BASE_URL")
print(f"BASEURL: {BASEURL}")
API_TOKEN=os.getenv("JAMF_API_TOKEN")
print(f"API_TOKEN: {API_TOKEN}")

SERIAL_TO_UDID_API_URL = f"{BASEURL}/devices/"
REMOVE_DEVICE_FROM_GROUP_API_URL = f"{BASEURL}/devices/groups/remove"
API_HEADERS = {
    "Authorization": f"Basic {API_TOKEN}",
    "Content-Type": "application/json"
}
CSV_FILE = "jamfscriptinput.csv"  # Your input file


ADD_TO_GROUP_API_URL = f"{BASEURL}/devices/groups/add"


# Sample list of serial numbers
serial_numbers = [
    "K233X7FXH5",
    "Q9JGJ2XXWH",
    "FQDWHV6Y4N"
]

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

def add_devices_to_group(udids, group_id):
    """Add a list of UDIDs to a device group."""
    payload = {
        "groupId": group_id,
        "udids": udids
    }
    print(payload)
    response = requests.post(ADD_TO_GROUP_API_URL, json=payload, headers=API_HEADERS)
    if response.status_code == 200:
        print("Successfully added devices to the group.")
    else:
        print(f"Failed to add devices to the group: {response.status_code}")
        print(response.text)

def remove_devices_from_group_by_udid(udids, group_id):
    payload = {
        "groupId": group_id,
	    "udids" : udids
	} 
    response = requests.post(REMOVE_DEVICE_FROM_GROUP_API_URL, json=payload, headers=API_HEADERS)
    if response.status_code == 200:
        print("Successfully removed devices from the group.")
    else:
        print(f"Failed to add devices to the group: {response.status_code}")
        print(response.text)
        

def read_serials_from_csv(filepath):
    """Read serial numbers from a CSV file with a column 'serial_number'."""
    serials = []
    with open(filepath, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            serial = row.get("serial_number")
            remove_group = row.get("remove_group")
            add_group = row.get("add_group")
            if serial:
                serials.append(serial.strip())
    return serials



def main():
    udids = []
    serial_numbers = read_serials_from_csv(CSV_FILE)
    for serial in serial_numbers:
        udid = get_udid_from_serial(serial)
        if udid:
            # remove_user_from_device_by_udid(udid)
            udids.append(udid)

    print(udids)

    DEVICE_GROUP_TO_REMOVE = 99
    DEVICE_GROUP_TO_ADD = 127
    if udids:
        remove_devices_from_group_by_udid(udids, DEVICE_GROUP_TO_REMOVE)
        add_devices_to_group(udids,DEVICE_GROUP_TO_ADD)
    else:
        print("No UDIDs collected. Nothing to change in the group.")

    # for udid in udids:
    #     remove_user_from_device(udid)

    # Uncomment this stuff if you want to add all the devices to a group.
    # Group must be created in JAMF, and group num must be set here
    # DEVICE_GROUP_ID = 124
    # if udids:
    #     add_devices_to_group(udids, DEVICE_GROUP_ID)
    # else:
    #     print("No UDIDs collected. Nothing to add to the group.")

if __name__ == "__main__":
    main()
