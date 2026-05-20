import os
import requests
import sys

# Configuration
BASE_URL=os.getenv("JAMF_BASE_URL")
# print(f"BASEURL: {BASE_URL}")
API_TOKEN=os.getenv("JAMF_API_TOKEN")
# print(f"API_TOKEN: {API_TOKEN}")

API_HEADERS = {
    "Authorization": f"Basic {API_TOKEN}",
    "X-Server-Protocol-Version": "4",
    "Content-Type": "application/json"
}

def get_users():
    # Step 1: Fetch all users
    print("Fetching users...")
    response = requests.get(f"{BASE_URL}/users", headers=API_HEADERS)
    response.raise_for_status()

    data = response.json()
    users = data["users"]
    if not users:
        print("No users found.")
        return

    print(f"Found {len(users)} user(s).")

    return users

def fix_whitespace(user):
    userID = user["id"]
    isDirty = False
    fields_to_clean = ["firstName", "lastName", "username"]

    for field in fields_to_clean:
        orig_val = user[field]
        clean_val = orig_val.strip()

        if clean_val != orig_val:
            isDirty = True

    if isDirty:
        payload = {
            "firstName": user["firstName"].strip(),
            "lastName": user["lastName"].strip(),
            "username": user["username"].strip()
        }
        print(f"Updating user {userID}: {user["username"]}")
        response = requests.put(f"{BASE_URL}/users/{userID}", json=payload, headers=API_HEADERS)

        if response.status_code == 200:
            print(f"Updated user")
            return True
        else:
            print(f"Failed to update user")
            print(payload)
            print(response.text)
            return False
    else:
        return False

if __name__ == "__main__":
    users= get_users()

    fixed_one = False
    for user in users:
#        if fixed_one == False:
            fixed_one = fix_whitespace(user)
