import requests
from bs4 import BeautifulSoup
from datetime import datetime
from io import StringIO
import pandas as pd
import sqlite3
import time
import re

CSV_URL = "https://www.police.pref.nagasaki.jp/police/wp-content/uploads/2026/08/nagasaki_2025zitensyatou.csv"

def normalize_town(town_raw):
    """
    町名を ●●町 に統一し、丁目を分離する
    """
    if town_raw is None:
        return None, None

    # 例: "浜町1丁目" → ("浜町", "1")
    m = re.match(r"(.+?町)(\d+)丁目", town_raw)
    if m:
        return m.group(1), m.group(2)

    # 例: "大橋町" → ("大橋町", None)
    if "町" in town_raw:
        return town_raw, None

    # 町名が入っていないケース
    return town_raw, None


def get_jitensha_theft():

    records = []

    print("Downloading:", CSV_URL)
    time.sleep(1)

    res = requests.get(CSV_URL)
    df = pd.read_csv(StringIO(res.text), encoding="shift_jis")

    for _, row in df.iterrows():

        town_raw = row.get("町丁目（発生地）", None)
        town_name, chome = normalize_town(town_raw)

        records.append({
            "city": row.get("市区町村（発生地）", None),
            "town": town_name,          # ●●町 に統一
            "chome": chome,             # 丁目（数字）
            "crime": row.get("手口", None),
            "date": row.get("発生年月日（始期）", None),
            "time": row.get("発生時（始期）", None),
            "place": row.get("発生場所", None),
            "detail": row.get("発生場所の詳細", None),
            "created_at": datetime.now().isoformat()
        })

    return records


def save_to_sqlite(records):
    conn = sqlite3.connect("nagasaki.db")
    df = pd.DataFrame(records)
    df.to_sql("crime_jitensha_raw", conn, if_exists="replace", index=False)
    conn.close()


records = get_jitensha_theft()
save_to_sqlite(records)

print("最新の自転車盗データをSQLiteへ保存しました。")
print(records[:5])