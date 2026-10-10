import sqlite3
from datetime import datetime

# hazard_raw.db から集計済みデータを読み込む
conn_raw = sqlite3.connect("hazard.db")
cur_raw = conn_raw.cursor()

cur_raw.execute("""
SELECT town_name, hazard_type, risk_ratio, risk_level, score_raw, score_std
FROM hazard_raw
""")

hazard_rows = cur_raw.fetchall()
conn_raw.close()

# town.db に書き込む
conn_town = sqlite3.connect("data/town.db")
cur_town = conn_town.cursor()

# town_name → town_id の辞書を作る
cur_town.execute("SELECT town_id, town_name FROM towns")
town_map = {name: tid for tid, name in cur_town.fetchall()}

# hazard_score に INSERT
for row in hazard_rows:
    town_name, hazard_type, risk_ratio, risk_level, score_raw, score_std = row

    # town_id を取得
    town_id = town_map.get(town_name)

    if town_id is None:
        print(f"⚠ 町名が town.db に存在しません: {town_name}")
        continue

    cur_town.execute("""
        INSERT INTO hazard_score (
            town_id, hazard_type, risk_ratio, risk_level,
            score_raw, score_std, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        town_id,
        hazard_type,
        risk_ratio,
        risk_level,
        score_raw,
        score_std,
        datetime.now().isoformat()
    ))

conn_town.commit()
conn_town.close()

print("hazard_score を town.db に書き込みました。")
