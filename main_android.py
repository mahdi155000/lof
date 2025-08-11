import requests
import os
from Asset import backend
from workspace_manager_module import workspace_manager

SERVER_URL = "http://192.168.1.142:5000"  # Change to your server's IP

def download_db():
    try:
        r = requests.get(SERVER_URL + "/api/download_db")
        with open("Asset/list_of_work.db", "wb") as f:
            f.write(r.content)
        print("Database downloaded from server.")
    except Exception as e:
        print("Download failed:", e)

def upload_db():
    try:
        with open("Asset/list_of_work.db", "rb") as f:
            files = {'dbfile': f}
            r = requests.post(SERVER_URL + "/api/upload_db", files=files)
        print("Database uploaded to server:", r.json())
    except Exception as e:
        print("Upload failed:", e)

def main():
    # Example usage
    while True:
        print("1. Download DB from server")
        print("2. Upload DB to server")
        print("3. Add work")
        print("4. View works")
        print("5. Exit")
        choice = input("Choose: ")
        if choice == "1":
            download_db()
        elif choice == "2":
            upload_db()
        elif choice == "3":
            text = input("Enter work: ")
            ws = workspace_manager.current_workspace
            backend.insert(titile=text, workspace=ws)
        elif choice == "4":
            ws = workspace_manager.current_workspace
            items = backend.view(ws)
            for item in items:
                print(item)
        elif choice == "5":
            break

if __name__ == "__main__":
    main()