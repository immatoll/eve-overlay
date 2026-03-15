import asyncio
import json
from pathlib import Path
import re
import os
import sqlite3
import time

import websockets

# -----------------------------
# Paths
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent
SYSTEM_LABELS_FILE = BASE_DIR / "data" / "labels_systems.json"
DB_FILE = BASE_DIR / "data" / "systems.db"

# Replace with your chat log folder
LOG_FOLDER = Path(os.path.expandvars(r"%USERPROFILE%\Documents\Frontier\logs\Chatlogs"))

# -----------------------------
# Globals
# -----------------------------
SYSTEM_IDS = {}
clients = set()
last_location_message = None
latest_file = None
current_system = None

# -----------------------------
# Load system labels
# -----------------------------
with open(SYSTEM_LABELS_FILE, "r", encoding="utf-8") as f:
    SYSTEM_IDS = json.load(f)

# -----------------------------
# SQLite helpers
# -----------------------------
def get_db():
    conn = sqlite3.connect(DB_FILE)
    return conn

def create_table_if_missing():
    columns = [f"data{i:02d} INTEGER DEFAULT 0" for i in range(1,31)]
    col_defs = ",\n".join(columns)
    sql = f"""
    CREATE TABLE IF NOT EXISTS systems (
        system_id INTEGER PRIMARY KEY,
        system_name TEXT,
        {col_defs}
    )
    """
    conn = get_db()
    conn.execute(sql)
    conn.commit()
    conn.close()

def insert_systems_if_missing():
    conn = get_db()
    for sid, name in SYSTEM_IDS.items():
        conn.execute("INSERT OR IGNORE INTO systems (system_id, system_name) VALUES (?,?)", (sid, name))
    conn.commit()
    conn.close()

def get_system_flags(system_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM systems WHERE system_id=?", (system_id,))
    row = cursor.fetchone()
    columns = [col[0] for col in cursor.description]
    conn.close()
    if not row:
        return None
    return dict(zip(columns, row))

def update_flag(system_id, column, value):
    if not column.startswith("data"):
        return False
    conn = get_db()
    conn.execute(f"UPDATE systems SET {column}=? WHERE system_id=?", (1 if value else 0, system_id))
    conn.commit() 
    conn.close()
    return True

# -----------------------------
# Utility: open log with correct encoding
# -----------------------------
def open_log(path):
    with open(path, "rb") as f:
        start = f.read(4)
    if start.startswith(b'\xff\xfe'):
        encoding = "utf-16"
    elif start.startswith(b'\xfe\xff'):
        encoding = "utf-16-be"
    elif start.startswith(b'\xef\xbb\xbf'):
        encoding = "utf-8-sig"
    else:
        encoding = "utf-8"
    return open(path, "r", encoding=encoding, errors="ignore")

# -----------------------------
# Broadcast current system to WebSocket clients
# -----------------------------
async def broadcast_system(system_name):
    global last_location_message
    system_id = None
    for sid, name in SYSTEM_IDS.items():
        if name == system_name:
            system_id = sid
            break
    if not system_id:
        system_id = "unknown"

    message = json.dumps({"system": system_name, "system_id": system_id})
    last_location_message = message

    if clients:
        await asyncio.gather(*(client.send(message) for client in clients))

# -----------------------------
# Watch chat log for location changes
# -----------------------------
async def watch_file(file_path):
    global current_system
    with open_log(file_path) as f:
        f.seek(0, 2)  # go to end
        while True:
            line = f.readline()
            if not line:
                await asyncio.sleep(0.5)
                continue
            match = re.search(r"Channel changed to Local : (.+)", line)
            if match:
                location = match.group(1).strip()
                if location != current_system:
                    current_system = location
                    print("Location changed:", location)
                    await broadcast_system(location)

# -----------------------------
# Find latest chat log file
# -----------------------------
def find_latest_file():
    files = list(LOG_FOLDER.glob("Local_*.txt"))
    if not files:
        return None
    return max(files, key=lambda f: f.stat().st_mtime)

# -----------------------------
# WebSocket handler
# -----------------------------
async def websocket_handler(websocket):
    clients.add(websocket)
    print("Client connected")

    # Send last known location immediately
    if last_location_message:
        await websocket.send(last_location_message)

    try:
        await websocket.wait_closed()
    finally:
        clients.remove(websocket)
        print("Client disconnected")

# -----------------------------
# Main function
# -----------------------------
async def main():
    global latest_file, current_system

    create_table_if_missing()
    insert_systems_if_missing()

    latest_file = find_latest_file()
    if not latest_file:
        print("No log files found!")
        return

    print("Watching file:", latest_file)

    # On start, get the last known location
    with open_log(latest_file) as f:
        lines = f.readlines()
        for line in reversed(lines):
            match = re.search(r"Channel changed to Local : (.+)", line)
            if match:
                current_system = match.group(1).strip()
                print("Initial location:", current_system)
                await broadcast_system(current_system)
                break

    # Start WebSocket server
    ws_server = await websockets.serve(websocket_handler, "localhost", 9001)

    # Start watching log file
    await watch_file(latest_file)

    await ws_server.wait_closed()

# -----------------------------
# Entry point
# -----------------------------
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exiting...")