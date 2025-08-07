import csv
import os
import requests

# Configuration
BASEURL=os.getenv("JAMF_BASE_URL")
print(f"BASEURL: {BASEURL}")
API_TOKEN=os.getenv("JAMF_API_TOKEN")
print(f"API_TOKEN: {API_TOKEN}")

SERIAL_TO_UDID_API_URL = f"{BASEURL}/devices/"
WIPE_API_URL = f"{BASEURL}/devices/" # Add UDID + '/wipe' to the end of this
API_HEADERS = {
    "Authorization": f"Basic {API_TOKEN}",
    "Content-Type": "application/json"
}
CSV_FILE = "jamfscriptinput.csv"  # Your input file

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
        

def read_serials_from_csv(filepath):
    """Read serial numbers from a CSV file with a column 'serial_number'."""
    serials = []
    with open(filepath, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            serial = row.get("serial_number")
            if serial:
                serials.append(serial.strip())
    return serials

def wipe_device_by_udid(udid):
    """Send the wipe device command to device"""
    payload = {
        "udids": udid
    }
    
    response = requests.post(f"{WIPE_API_URL}{udid}/wipe", json=payload, headers=API_HEADERS)
    if response.status_code == 200:
        print("Successfully sent 'wipe device' command.")
    else:
        print(f"Failed to send 'wipe device' command: {response.status_code}")
        print(response.text)


def main():
    udids = []
    serial_numbers = read_serials_from_csv(CSV_FILE)
    for serial in serial_numbers:
        udid = get_udid_from_serial(serial)
        if udid:
            wipe_device_by_udid(udid)
            udids.append(udid)

    # print(udids)


if __name__ == "__main__":
    main()
