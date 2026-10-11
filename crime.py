import requests
from bs4 import BeautifulSoup
from datetime import datetime
from io import StringIO
import pandas as pd
import sqlite3
import time
import re

CSV_URL = {
    "自転車盗": "https://www.police.pref.nagasaki.jp/police/wp-content/uploads/2026/08/nagasaki_2025zitensyatou.csv",
    "ひったくり": "https://www.police.pref.nagasaki.jp/police/wp-content/uploads/2026/08/nagasaki_2025hittakuri.csv",
}

def normalize_town(town_raw):
    if town_raw is None or isinstance(town_raw, float):
        return None, None

    town_raw = str(town_raw)

    m = re.match(r"(.+?町)(\d+)丁目", town_raw)
    if m:
        return m.group(1), m.group(2)

    m2 = re.match(r"(.+?)(\d+)丁目", town_raw)
    if m2:
        return m2.group(1), m2.group(2)

    if "町" in town_raw:
        return town_raw, None

    return town_raw, None


def load_crime_csv(crime_type, url):
    print(f"Downloading: {crime_type} → {url}")
    time.sleep(1)

    res = requests.get(url)
    df = pd.read_csv(StringIO(res.text), encoding="shift_jis")

    df["町丁目（発生地）"] = df["町丁目（発生地）"].fillna("")

    records = []

    for _, row in df.iterrows():
        town_raw = row.get("町丁目（発生地）", None)
        town_name, chome = normalize_town(town_raw)

        records.append({
            "crime_type": crime_type,
            "city": row.get("市区町村（発生地）", None),
            "town": town_name,
            "chome": chome,
            "crime": row.get("手口", None),
            "date": row.get("発生年月日（始期）", None),
            "place": row.get("発生場所", None),
            "detail": row.get("発生場所の詳細", None),
            "created_at": datetime.now().isoformat()
        })

    return records


def save_all_crimes_to_sqlite(all_records):
    conn = sqlite3.connect("crime.db")
    df = pd.DataFrame(all_records)
    df.to_sql("crime_raw_all", conn, if_exists="replace", index=False)
    conn.close()
    print("全犯罪種別の raw データを crime_raw_all に保存しました。")


def save_stats_to_sqlite():
    conn = sqlite3.connect("crime.db")
    df = pd.read_sql("SELECT * FROM crime_raw_all", conn)

    stats = (
        df.groupby(["town", "crime_type"])
          .size()
          .reset_index(name="count")
          .sort_values("count", ascending=False)
    )

    stats.to_sql("crime_stats_all", conn, if_exists="replace", index=False)
    conn.close()

    print("町 × 犯罪種別の crime_stats_all を作成しました。")


# 実行
all_records = []

for crime_type, url in CSV_URL.items():
    records = load_crime_csv(crime_type, url)
    all_records.extend(records)

save_all_crimes_to_sqlite(all_records)
save_stats_to_sqlite()

print("全犯罪種別の処理が完了しました。")
print(all_records[:5])

