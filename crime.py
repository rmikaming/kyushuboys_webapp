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
    （既存ロジックを残しつつ、町が付かない丁目にも対応）
    """
    if town_raw is None or isinstance(town_raw, float):
        return None, None

    town_raw = str(town_raw)

    # ① 既存ロジック（浜町1丁目 → 浜町, 1）
    m = re.match(r"(.+?町)(\d+)丁目", town_raw)
    if m:
        return m.group(1), m.group(2)

    # ② 新規追加：町が付かない丁目（中川2丁目 → 中川, 2）
    m2 = re.match(r"(.+?)(\d+)丁目", town_raw)
    if m2:
        return m2.group(1), m2.group(2)

    # ③ 既存ロジック（大橋町 → 大橋町, None）
    if "町" in town_raw:
        return town_raw, None

    # ④ その他（町名が入っていないケース）
    return town_raw, None


def get_jitensha_theft():

    records = []

    print("Downloading:", CSV_URL)
    time.sleep(1)

    res = requests.get(CSV_URL)
    df = pd.read_csv(StringIO(res.text), encoding="shift_jis")

    df["町丁目（発生地）"] = df["町丁目（発生地）"].fillna("")

    for _, row in df.iterrows():

        town_raw = row.get("町丁目（発生地）", None)
        town_name, chome = normalize_town(town_raw)

        records.append({
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



def save_to_sqlite(records):
    conn = sqlite3.connect("crime.db")
    df = pd.DataFrame(records)
    df.to_sql("crime_jitensha_raw", conn, if_exists="replace", index=False)
    conn.close()

def save_stats_to_sqlite():
    conn = sqlite3.connect("crime.db")

    # 正しいテーブル名に修正
    df = pd.read_sql("SELECT * FROM crime_jitensha_raw", conn)

    # 町別に件数を集計
    stats = (
        df.groupby("town")
          .size()
          .reset_index(name="count")
          .sort_values("count", ascending=False)
    )

    # crime_stats テーブルとして保存（上書き）
    stats.to_sql("crime_stats", conn, if_exists="replace", index=False)

    conn.close()
    print("町別犯罪件数テーブル（crime_stats）を作成しました。")




records = get_jitensha_theft()
save_to_sqlite(records)
save_stats_to_sqlite()   # ← これを追加

print("最新の自転車盗データをSQLiteへ保存しました。")
print(records[:5])

