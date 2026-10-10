import sqlite3

conn = sqlite3.connect("data/town.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS towns (
    town_id INTEGER PRIMARY KEY AUTOINCREMENT,
    town_name TEXT,
    representative_address TEXT,
    lat REAL,
    lon REAL,
    area_km2 REAL,
    geom_json TEXT,
    updated_at TEXT
)
""")

conn.commit()
conn.close()

print("towns テーブルを作成しました。")
