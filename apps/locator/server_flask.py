from flask import Flask, jsonify
from flask_cors import CORS
import sqlite3
from pathlib import Path
from flask import request

BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "data" / "systems.db"

app = Flask(__name__)

CORS(app)

def get_db():
    return sqlite3.connect(DB_FILE)


@app.route("/system/<int:system_id>")
def get_system(system_id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM systems
        WHERE system_id = ?
    """, (system_id,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "not found"}), 404

    columns = [col[0] for col in cursor.description]

    result = dict(zip(columns, row))

    return jsonify(result)

@app.route("/system/<int:system_id>/toggle", methods=["POST"])
def toggle_data(system_id):

    column = request.json.get("column")
    value = request.json.get("value")

    if not column.startswith("data"):
        return jsonify({"error": "invalid column"}), 400

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        f"UPDATE systems SET {column} = ? WHERE system_id = ?",
        (1 if value else 0, system_id)
    )

    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(port=9500)