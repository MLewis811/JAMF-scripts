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
    "X-Server-Protocol-Version": "4",
    "Content-Type": "application/json"
}

DEFAULT_CSV_FILE = "jamfscriptinput.csv"

GET_USERS_API_URL = f"{BASEURL}/users/"
CREATE_CLASSES_API_URL = f"{BASEURL}/classes"
GET_CLASSES_API_URL = f"{BASEURL}/classes"


def read_data_from_csv(filepath):
    """Read names from a column 'last_first'."""
    names = []
    """Read groups from a column 'group'."""
    groups = []


    with open(filepath, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name = row.get("last_first")
            names.append(name)

            group = row.get("group")
            groups.append(group)
    return names, groups

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
    
def get_userId_by_username(name, users):
    for user in users:
        if user["username"] == name:
            return(user["id"])
        
    return None

def make_lastFirst_into_firstLast(name):
    last, first = name.split(",")
    new_name = f"{first.strip()} {last.strip()}"
    return new_name

def createClass(tchrID, tchrLast):
    className = f"2526 {tchrLast}"
    print(f"Creating class {className} with teacher {tchrID}")
    payload = {
        "name": className,
        "teachers": [
            tchrID
        ]
    }
    response = requests.post(f"{CREATE_CLASSES_API_URL}", json=payload, headers=API_HEADERS)
    if response.status_code == 200:
        responseData = response.json()
        uuid = responseData["uuid"]
        print(f"Created class {uuid}")
        return uuid
    else:
        print("Failed to create class")
        print(response.text)
        return None

def getUserGroupIDForClassByUUID(uuid):
    response = requests.get(f"{GET_CLASSES_API_URL}/{uuid}", headers=API_HEADERS)
    if response.status_code == 200:
        data = response.json()
        userGroupID = data["class"]["userGroupId"]
        return userGroupID
    else:
        print(f"Failed to get groups: {response.status_code}")
        return None



def addUserAsStudentToClass(studentID, classID):
    payload = {
        "students": [
            studentID
        ]
    }
    response = requests.put(f"{CREATE_CLASSES_API_URL}/{classID}/users", json=payload, headers=API_HEADERS)
    if response.status_code == 200:
        responseData = response.json()
        print(f"Added student {studentID} to {classID}" )
    else:
        print("Failed to add student to class")
        print(response.text)

def main():
    users = get_users()

    # If a filename is given on the command line, use it; otherwise use default
    csv_file = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CSV_FILE

    names, groups = read_data_from_csv(csv_file)

    for i, name in enumerate(names):
        if groups[i] == "Staff iPads":
            tchrLastFirst = name
            tchrLast, tchrFirst = tchrLastFirst.split(",")
            tchrFirstLast = make_lastFirst_into_firstLast(tchrLastFirst)
            tchrID = get_userId_by_username(tchrFirstLast, users)
            classUUID = createClass(tchrID, tchrLast.strip())
            if classUUID:
                userGroupID = getUserGroupIDForClassByUUID(classUUID)
                print(userGroupID)
        else:
            studentLastFirst = name
            studentFirstLast = make_lastFirst_into_firstLast(studentLastFirst)
            studentID = get_userId_by_username(studentFirstLast, users)
            if studentID:
                print(f"Adding {studentLastFirst} to class {classUUID}")
                addUserAsStudentToClass(studentID, classUUID)




            else:
                print(f"************* student not found: {studentLastFirst}")



if __name__ == "__main__":
    main()



