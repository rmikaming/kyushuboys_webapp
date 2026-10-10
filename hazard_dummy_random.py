# 保存ファイル名：hazard_dummy_random.py

import sqlite3
import random

DB_PATH = r"C:\Users\star_\OneDrive\Desktop\git作業用\テスト１\kyushuboys_webapp\data\town.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("SELECT town_id FROM towns")
towns = cur.fetchall()

for (town_id,) in towns:
    flood = random.randint(0, 5)
    landslide = random.randint(0, 5)
    quake = random.randint(0, 5)
    score = flood + landslide + quake

    cur.execute("""
        UPDATE towns
        SET hazard_flood = ?, hazard_landslide = ?, hazard_quake = ?, hazard_score = ?
        WHERE town_id = ?
    """, (flood, landslide, quake, score, town_id))

conn.commit()
conn.close()

print("ランダム仮ハザード値を towns に登録しました。")
