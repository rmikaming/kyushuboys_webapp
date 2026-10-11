import sqlite3
import pandas as pd
from hazard_score import calculate_hazard_score
from database import DB_PATH

print("🌪 ハザードスコアを town.db に追加します...")

# hazard_score を計算（DataFrame）
hazard_df = calculate_hazard_score()

# DB 接続
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# 必要なカラムを追加（存在しない場合のみ）
columns = [
    "hazard_flood INTEGER",
    "hazard_landslide INTEGER",
    "hazard_quake INTEGER",
    "hazard_level INTEGER",
    "hazard_score REAL"
]

for col in columns:
    try:
        cur.execute(f"ALTER TABLE town ADD COLUMN {col};")
        print(f"Added column: {col}")
    except:
        print(f"Column already exists: {col}")

# town テーブルを更新
for _, row in hazard_df.iterrows():
    cur.execute("""
        UPDATE town SET
            hazard_flood = ?,
            hazard_landslide = ?,
            hazard_quake = ?,
            hazard_level = ?,
            hazard_score = ?
        WHERE town_name = ?
    """, (
        row["hazard_flood"],
        row["hazard_landslide"],
        row["hazard_quake"],
        row["hazard_level"],
        row["hazard_score"],
        row["town_name"]
    ))

conn.commit()
conn.close()

print("🎉 ハザードスコアのセットアップが完了しました！")
