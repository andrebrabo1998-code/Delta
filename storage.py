import json
import os
from datetime import datetime

DB_FILE = "db.json"

def load():
    if not os.path.exists(DB_FILE):
        return []
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

def append(record):
    data = load()
    data.append(record)
    save(data)

def now_iso():
    return datetime.utcnow().isoformat()
