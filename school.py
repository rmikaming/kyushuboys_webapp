import sqlite3
from datetime import datetime
import re


# 諫早市公式サイトには小学校の住所一覧ページが存在しないため、
# Googleマップで確認した住所を手動で収集してDBに保存する。
# 諫早市の住所は「○○町△△」のように町名の後に字（地区名）が続く場合があるため、
# 町＋字まで抽出できるように正規表現を調整している。

schools = [
    {"name": "諫早市立諫早小学校", "address": "長崎県諫早市仲沖町457-4", "population": 395,"ido": 32.844264, "keido": 130.068644},
    {"name": "諫早市立北諫早小学校", "address": "長崎県諫早市金谷町1-1", "population": 658,"ido": 32.849947, "keido": 130.050379},
    {"name": "諫早市立小栗小学校", "address": "長崎県諫早市小川町9", "population": 407,"ido": 32.831737, "keido": 130.060651},
    {"name": "諫早市立上諫早小学校", "address": "長崎県諫早市本99-2", "population": 76,"ido": 32.865847, "keido": 130.041266},
    {"name": "諫早市立本野小学校", "address": "長崎県諫早市本野町94", "population": 66,"ido": 32.893824, "keido": 130.025336},
    {"name": "諫早市立小野小学校", "address": "長崎県諫早市宗方町365", "population": 292,"ido": 32.832379, "keido": 130.085757},
    {"name": "諫早市立喜々津小学校", "address": "長崎県諫早市多良見町中里27", "population": 511,"ido": 32.825734, "keido": 129.975761},
    {"name": "諫早市立西諫早小学校", "address": "長崎県諫早市馬渡町3", "population": 385,"ido": 32.845433, "keido": 130.026684},
    {"name": "諫早市立森山東小学校", "address": "長崎県諫早市森山町杉谷2343", "population": 110,"ido": 32.81088, "keido": 130.135414},
    {"name": "諫早市立森山西小学校", "address": "長崎県諫早市森山町下井牟田473-1", "population": 136,"ido": 32.825095, "keido": 130.115719},
    {"name": "諫早市立高来西小学校", "address": "長崎県諫早市高来町峰50-1", "population": 168,"ido": 32.890609, "keido": 130.109484},
    {"name": "諫早市立真津山小学校", "address": "長崎県諫早市貝津町715-2", "population": 676,"ido": 32.83601, "keido": 130.006925},
    {"name": "諫早市立飯盛東小学校", "address": "長崎県諫早市飯盛町中山653", "population": 299,"ido": 32.782692, "keido": 130.022372},
    {"name": "諫早市立飯盛西小学校", "address": "長崎県諫早市飯盛町里620", "population": 68,"ido": 32.770132, "keido": 129.993736},
    {"name": "諫早市立有喜小学校", "address": "長崎県諫早市有喜町800 ", "population": 148,"ido": 32.796042, "keido": 130.077482},
    {"name": "諫早市立御立山小学校", "address": "長崎県諫早市西栄田町1250-4", "population": 771,"ido": 32.856176, "keido": 130.031958},
    {"name": "諫早市立長田小学校", "address": "長崎県諫早市西里町800", "population": 241,"ido": 32.862946, "keido": 130.075126},
    {"name": "諫早市立真崎小学校", "address": "長崎県諫早市宗白岩町3-1", "population": 120,"ido": 32.847315, "keido": 130.021568},
    {"name": "諫早市立真城小学校", "address": "長崎県諫早市小野真崎町1037-3", "population": 341,"ido": 32.85179, "keido": 130.018838},
    {"name": "諫早市立みはる台小学校", "address": "長崎県諫早市平山町200-3", "population": 175,"ido": 32.83166, "keido": 130.038358},
    {"name": "諫早市立小長井小学校", "address": "長崎県諫早市小長井町小川原浦958", "population": 142,"ido": 32.920557, "keido": 130.185765},
    {"name": "諫早市立湯江小学校", "address": "長崎県諫早市高来町三部壱553", "population": 270,"ido": 32.909933, "keido": 130.142042},
    {"name": "諫早市立伊木力小学校", "address": "長崎県諫早市多良見町舟津1107-1", "population": 53,"ido": 32.8585455, "keido": 129.928676},
    {"name": "諫早市立大草小学校", "address": "長崎県諫早市多良見町野副59", "population": 28,"ido": 32.845781, "keido": 129.952741},
    {"name": "諫早市立喜々津東小学校", "address": "長崎県諫早市多良見町シーサイド1-286", "population": 274,"ido": 32.838238, "keido": 129.992607},
    {"name": "諫早市立上山小学校", "address": "長崎県諫早市西小路町1031-1", "population": 401,"ido": 32.839845, "keido": 130.39704}


]

# 町＋字まで抽出する（数字が出る前まで）
def extract_town(address):
    m = re.search(r"諫早市(.+?町[^\d]+)", address)
    if m:
        return m.group(1)

    m2 = re.search(r"諫早市(.+?町)", address)
    if m2:
        return m2.group(1)

    return None

# school.db のテーブル作成（school に変更）
def init_db():
    conn = sqlite3.connect("school.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS school (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            address TEXT,
            town TEXT,
            population INTEGER,
            ido REAL,
            keido REAL,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

# 手動収集データを school テーブルに登録
def sync_db():
    conn = sqlite3.connect("school.db")
    cur = conn.cursor()

    cur.execute("DELETE FROM school")

    for s in schools:
        town = extract_town(s["address"])
        cur.execute("""
            INSERT INTO school (name, address, town, population, ido, keido, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            s["name"],
            s["address"],
            town,
            s["population"],
            s["ido"],
            s["keido"],
            datetime.now().isoformat()
        ))

    conn.commit()
    conn.close()

# 実行関数
def update_school_db():
    init_db()
    sync_db()
    print("諫早市の小学校データ（町＋字抽出版）を school テーブルに保存しました。")

def copy_town_table():
    # 2つのDBを開く
    conn_town = sqlite3.connect("data/town.db")
    conn_school = sqlite3.connect("school.db")

    cur_town = conn_town.cursor()
    cur_school = conn_school.cursor()

    # school.db に新しいテーブルを作成（なければ）
    cur_school.execute("""
        CREATE TABLE IF NOT EXISTS school_town (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            town_name TEXT
        )
    """)

    # school_town を初期化
    cur_school.execute("DELETE FROM school_town")

    # town.db から town_name を取得
    cur_town.execute("SELECT town_name FROM town")
    rows = cur_town.fetchall()

    # school.db にコピー
    for row in rows:
        cur_school.execute(
            "INSERT INTO school_town (town_name) VALUES (?)",
            (row[0],)   # ← 値は1つだけ
        )

    conn_school.commit()
    conn_town.close()
    conn_school.close()

    print("town_name を school.db の新しいテーブルに保存しました。")

def add_lat_lon_columns():
    conn = sqlite3.connect("school.db")
    cur = conn.cursor()

    # lat / lon カラムを追加
    cur.execute("ALTER TABLE school_town ADD COLUMN lat REAL")
    cur.execute("ALTER TABLE school_town ADD COLUMN lon REAL")

    conn.commit()
    conn.close()

    print("school_town に lat / lon カラムを追加しました。")


import csv

def update_town_latlon_from_csv(csv_path):
    conn = sqlite3.connect("school.db")
    cur = conn.cursor()

    with open(csv_path, encoding="cp932") as f:
        reader = csv.DictReader(f)

        for row in reader:
            # CSV の町名を前後の空白を除去
            town_name = row["大字町丁目名"].strip()

            lat = float(row["緯度"])
            lon = float(row["経度"])

            # school_town の town_name も strip して比較
            cur.execute("""
                UPDATE school_town
                SET lat = ?, lon = ?
                WHERE TRIM(town_name) = ?
                   OR town_name LIKE '%' || ? || '%'
            """, (lat, lon, town_name, town_name))

    conn.commit()
    conn.close()

    print("CSV の座標を school_town に反映しました。")

from geopy.distance import geodesic
def calc_distance_town_school():
    conn = sqlite3.connect("school.db")
    cur = conn.cursor()

    # school_town の座標を取得
    cur.execute("SELECT town_name, lat, lon FROM school_town")
    towns = cur.fetchall()

    # school の座標を取得
    cur.execute("SELECT name, ido, keido FROM school")
    schools = cur.fetchall()

    results = []

    for town_name, t_lat, t_lon in towns:
        # 座標が入っていない町はスキップ
        if t_lat is None or t_lon is None:
            continue

        for school_name, s_lat, s_lon in schools:
            dist = geodesic((t_lat, t_lon), (s_lat, s_lon)).km

            results.append({
                "town": town_name,
                "school": school_name,
                "distance_km": dist
            })

    # 結果を新しいテーブルに保存
    cur.execute("""
        CREATE TABLE IF NOT EXISTS town_school_distance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            town_name TEXT,
            school_name TEXT,
            distance_km REAL
        )
    """)

    cur.execute("DELETE FROM town_school_distance")

    for r in results:
        cur.execute("""
            INSERT INTO town_school_distance (town_name, school_name, distance_km)
            VALUES (?, ?, ?)
        """, (r["town"], r["school"], r["distance_km"]))

    conn.commit()
    conn.close()

    print("町 × 小学校の距離計算が完了しました。")

def extract_nearest_school():
    conn = sqlite3.connect("school.db")
    cur = conn.cursor()

    cur.execute("""
        SELECT town_name, school_name, distance_km
        FROM town_school_distance
        WHERE distance_km = (
            SELECT MIN(distance_km)
            FROM town_school_distance AS t2
            WHERE t2.town_name = town_school_distance.town_name
        )
        ORDER BY town_name;
    """)
    rows = cur.fetchall()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS nearest_school (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            town_name TEXT,
            school_name TEXT,
            distance_km REAL
        )
    """)
    cur.execute("DELETE FROM nearest_school")

    for town_name, school_name, dist in rows:
        cur.execute("""
            INSERT INTO nearest_school (town_name, school_name, distance_km)
            VALUES (?, ?, ?)
        """, (town_name, school_name, dist))

    conn.commit()
    conn.close()

    print("町ごとの最寄り小学校を nearest_school に保存しました。")

def ensure_score_column():
    conn = sqlite3.connect("school.db")
    cur = conn.cursor()

    cur.execute("PRAGMA table_info(town_school_distance)")
    columns = [row[1] for row in cur.fetchall()]

    if "score" not in columns:
        cur.execute("ALTER TABLE town_school_distance ADD COLUMN score REAL")
        print("score カラムを追加しました")
    else:
        print("score カラムは既に存在します")

    conn.commit()
    conn.close()


def ensure_nearest_score_column():
    conn = sqlite3.connect("school.db")
    cur = conn.cursor()

    cur.execute("PRAGMA table_info(nearest_school)")
    columns = [row[1] for row in cur.fetchall()]

    if "score" not in columns:
        cur.execute("ALTER TABLE nearest_school ADD COLUMN score REAL")
        print("nearest_school に score カラムを追加しました")
    else:
        print("nearest_school に score カラムは既に存在します")

    conn.commit()
    conn.close()

def update_nearest_score():
    conn = sqlite3.connect("school.db")
    cur = conn.cursor()

    cur.execute("SELECT id, distance_km FROM nearest_school")
    rows = cur.fetchall()

    for row_id, dist in rows:
        if dist < 0.5:
            score = 10
        elif dist < 1.0:
            score = 5
        else:
            score = 2

        cur.execute("""
            UPDATE nearest_school
            SET score = ?
            WHERE id = ?
        """, (score, row_id))

    conn.commit()
    conn.close()

    print("nearest_school の距離スコアを反映しました。")


def update_distance_score():
    conn = sqlite3.connect("school.db")
    cur = conn.cursor()

    cur.execute("SELECT id, distance_km FROM town_school_distance")
    rows = cur.fetchall()

    for row_id, dist in rows:
        if dist < 0.5:
            score = 10
        elif dist < 1.0:
            score = 5
        else:
            score = 2

        cur.execute("""
            UPDATE town_school_distance
            SET score = ?
            WHERE id = ?
        """, (score, row_id))

    conn.commit()
    conn.close()

    print("town_school_distance の距離スコアを反映しました。")







if __name__ == "__main__":
    update_school_db()
    copy_town_table()
    update_town_latlon_from_csv("諫早市座標.csv")
    calc_distance_town_school()
    extract_nearest_school()
  

    ensure_score_column()
    update_distance_score()

    ensure_nearest_score_column()
    update_nearest_score()



