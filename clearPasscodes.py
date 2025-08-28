import csv
import os
import requests

# Configuration
BASEURL=os.getenv("JAMF_BASE_URL")
print(f"BASEURL: {BASEURL}")
API_TOKEN=os.getenv("JAMF_API_TOKEN")
print(f"API_TOKEN: {API_TOKEN}")

LIST_DEVICES_API_URL = f"{BASEURL}/devices"
API_HEADERS = {
    "Authorization": f"Basic {API_TOKEN}",
    "Content-Type": "application/json"
}
CSV_FILE = "jamfscriptinput.csv"  # Your input file


def get_udids_for_devices():
    udids = []
    response = requests.get(f"{LIST_DEVICES_API_URL}", headers=API_HEADERS)
    if response.status_code == 200:
        data = response.json()
        devCount = data["count"]
        print(f"{devCount} devices found")
        if devCount > 0:
            deviceList = data["devices"]
            for device in deviceList:
                udids.append(device.get("UDID"))
    else:
        print("Failed to retrieve any devices")
    return udids

def get_devices_with_passcode():
    pcSerials = []
    udids = get_udids_for_devices()
    for udid in udids:
        response = requests.get(f"{LIST_DEVICES_API_URL}/{udid}", headers=API_HEADERS)
        if response.status_code == 200:
            data = response.json()
            device = data["device"]
            if "hasPasscode" in device:
                hasPass = device["hasPasscode"]
                if hasPass is True :
                    pcSerials.append(device["serialNumber"])
                    print(f"{pcSerials.count}: {udid} {hasPass}")
            else:
                print(f"{udid} doesn't have the 'hasPasscode' field.")
        else:
            print(f"Failed to retrieve info about {udid}")

    return pcSerials

def main():
    pcSerials = get_devices_with_passcode()
    print(pcSerials)



if __name__ == "__main__":
    main()
