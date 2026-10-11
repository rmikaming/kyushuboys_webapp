import sqlite3
import pandas as pd
from hazard_score import calculate_hazard_score
from database import DB_PATH

print("🌪 ハザードスコアを hazard テーブルに追加します...")

# hazard_score を計算（DataFrame）
hazard_df = calculate_hazard_score()

# DB 接続
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# hazard 専用テーブルを作成（存在しない場合のみ）
cur.execute("""
CREATE TABLE IF NOT EXISTS hazard (
    town_name TEXT PRIMARY KEY,
    hazard_flood INTEGER,
    hazard_landslide INTEGER,
    hazard_tsunami INTEGER,
    hazard_level REAL,
    hazard_score REAL
);
""")

# hazard テーブルを更新（INSERT OR REPLACE）
for _, row in hazard_df.iterrows():
    cur.execute("""
        INSERT OR REPLACE INTO hazard (
            town_name,
            hazard_flood,
            hazard_landslide,
            hazard_tsunami,
            hazard_level,
            hazard_score
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (
        row["town_name"],
        row["hazard_flood"],
        row["hazard_landslide"],
        row["hazard_quake"],
        row["hazard_level"],
        row["hazard_score"]
    ))

conn.commit()
conn.close()

print("🎉 hazard テーブルへのセットアップが完了しました！")


