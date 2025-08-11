import requests
import sqlite3
import os

SERVER_URL = "http://192.168.1.142:5000"  # Change to your server's IP
LOCAL_DB = "list_of_work.db"

def download_db():
    try:
        r = requests.get(SERVER_URL + "/api/download_db")
        with open(LOCAL_DB, "wb") as f:
            f.write(r.content)
        print("Database downloaded from server and saved locally as", LOCAL_DB)
    except Exception as e:
        print("Download failed:", e)

def upload_db():
    try:
        with open(LOCAL_DB, "rb") as f:
            files = {'dbfile': f}
            r = requests.post(SERVER_URL + "/api/upload_db", files=files)
        print("Database uploaded to server:", r.json())
    except Exception as e:
        print("Upload failed:", e)

def view_works():
    if not os.path.exists(LOCAL_DB):
        print("No local database found. Download it first.")
        return
    conn = sqlite3.connect(LOCAL_DB)
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM lof")  # Change 'lof' to your table name if different
        rows = cur.fetchall()
        for row in rows:
            print(row)
    except Exception as e:
        print("Error reading database:", e)
    conn.close()

def add_work(text):
    if not os.path.exists(LOCAL_DB):
        print("No local database found. Download it first.")
        return
    conn = sqlite3.connect(LOCAL_DB)
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO lof (title) VALUES (?)", (text,))  # Add other fields if needed
        conn.commit()
        print("Work added locally.")
    except Exception as e:
        print("Error adding work:", e)
    conn.close()

def main():
    while True:
        print("\n1. Download DB from server")
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
            add_work(text)
        elif choice == "4":
            view_works()
        elif choice == "5":
            break

if __name__ == "__main__":
    main()