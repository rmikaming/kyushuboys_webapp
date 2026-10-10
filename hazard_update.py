import sqlite3
import requests
import time
from datetime import datetime

DB_PATH = r"C:\Users\star_\OneDrive\Desktop\git作業用\テスト１\kyushuboys_webapp\data\town.db"

def get_hazard(lat, lon):
    url = f"https://disaportaldata.mlit.go.jp/risksearch/latlon?lat={lat}&lon={lon}"
    res = requests.get(url)
    data = res.json()

    if "result" not in data or len(data["result"]) == 0:
        return None

    return data["result"][0]


conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("SELECT town_id, lat, lon FROM towns WHERE lat IS NOT NULL AND lon IS NOT NULL")
towns = cur.fetchall()

for town_id, lat, lon in towns:

    hazard = get_hazard(lat, lon)

    if hazard is None:
        print(f"ハザード取得失敗: town_id={town_id}")
        continue

    flood = hazard.get("flood", None)
    landslide = hazard.get("landslide", None)
    quake = hazard.get("quake", None)

    # スコア化（例：単純合計）
    hazard_score = sum([
        flood if isinstance(flood, (int, float)) else 0,
        landslide if isinstance(landslide, (int, float)) else 0,
        quake if isinstance(quake, (int, float)) else 0
    ])

    cur.execute("""
        UPDATE towns
        SET hazard_flood = ?, hazard_landslide = ?, hazard_quake = ?, hazard_score = ?, updated_at = ?
        WHERE town_id = ?
    """, (
        flood,
        landslide,
        quake,
        hazard_score,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        town_id
    ))

    conn.commit()
    print(f"ハザード登録成功: town_id={town_id} → score={hazard_score}")

    time.sleep(0.5)

conn.close()
print("全町名のハザード登録が完了しました。")
