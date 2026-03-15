import json
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

JSON_FILE = BASE_DIR / "labels_systems.json"
DB_FILE = BASE_DIR / "systems.db"

TABLE_NAME = "systems"


def create_table(conn):

    columns = []
    for i in range(1, 31):
        columns.append(f"data{i:02d} TEXT")

    data_columns = ",\n".join(columns)

    sql = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        system_id INTEGER PRIMARY KEY,
        system_name TEXT,
        {data_columns}
    )
    """

    conn.execute(sql)


def insert_systems(conn, systems):

    sql = f"""
    INSERT OR IGNORE INTO {TABLE_NAME} (system_id, system_name)
    VALUES (?, ?)
    """

    for system_id, name in systems.items():
        conn.execute(sql, (system_id, name))

    conn.commit()


def main():

    print("Loading system labels...")

    with open(JSON_FILE, "r", encoding="utf-8") as f:
        systems = json.load(f)

    print("Creating database...")

    conn = sqlite3.connect(DB_FILE)

    create_table(conn)
    insert_systems(conn, systems)

    conn.close()

    print("Database created:", DB_FILE)


if __name__ == "__main__":
    main()