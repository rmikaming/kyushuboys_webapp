import sqlite3
import os
import pandas as pd

from hazard_score import calculate_hazard_score
from traffic_score import calculate_traffic_score

# -----------------------------
# town.db のセットアップ
# -----------------------------
def setup_town_db():
    if not os.path.exists("data"):
        os.makedirs("data")

    conn = sqlite3.connect("data/town.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS towns (
        town_name TEXT PRIMARY KEY,
        town_area_name TEXT,
        lat REAL,
        lon REAL,
        area REAL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS traffic (
        town_name TEXT PRIMARY KEY,
        route_count INTEGER,
        bus_stop_count INTEGER,
        traffic_score REAL
    );
    """)

    conn.commit()
    conn.close()
    print("✔ town.db のセットアップ完了")


# -----------------------------
# score.db のセットアップ
# -----------------------------
def setup_score_db():
    conn = sqlite3.connect("data/score.db")
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS score")

    cur.execute("""
    CREATE TABLE score (
        town_name TEXT PRIMARY KEY,
        hospital_score REAL,
        school_score REAL,
        crime_score REAL,
        bus_score REAL,
        hazard_score REAL,
        traffic_score REAL,
        area REAL
    );
    """)

    conn.commit()
    conn.close()
    print("✔ score.db のセットアップ完了")


# -----------------------------
# town_name を score.db に登録
# -----------------------------
def insert_town_names():
    conn_town = sqlite3.connect("data/town.db")
    towns = pd.read_sql("SELECT town_name FROM towns", conn_town)
    conn_town.close()

    conn_score = sqlite3.connect("data/score.db")
    cur = conn_score.cursor()

    for _, row in towns.iterrows():
        cur.execute("""
            INSERT OR IGNORE INTO score (town_name)
            VALUES (?);
        """, (row["town_name"],))

    conn_score.commit()
    conn_score.close()

    print("✔ score.db に町名を登録しました")


# -----------------------------
# area の統合
# -----------------------------
def write_area():
    conn_town = sqlite3.connect("data/town.db")
    df_town = pd.read_sql("SELECT town_name, area FROM towns", conn_town)
    conn_town.close()

    conn_score = sqlite3.connect("data/score.db")
    cur = conn_score.cursor()

    for _, row in df_town.iterrows():
        cur.execute("""
            UPDATE score
            SET area = ?
            WHERE town_name = ?
        """, (row["area"], row["town_name"]))

    conn_score.commit()
    conn_score.close()

    print("✔ area を score.db に統合しました")


# -----------------------------
# hazard_score の統合
# -----------------------------
def write_hazard_score():
    df = calculate_hazard_score()

    conn = sqlite3.connect("data/score.db")
    cur = conn.cursor()

    for _, row in df.iterrows():
        cur.execute("""
            UPDATE score
            SET hazard_score = ?
            WHERE town_name = ?
        """, (float(row["hazard_score"]), row["town_name"]))

    conn.commit()
    conn.close()

    print("✔ hazard_score を統合しました")


# -----------------------------
# traffic_score の統合
# -----------------------------
def write_traffic_score():
    df = calculate_traffic_score()

    conn = sqlite3.connect("data/score.db")
    cur = conn.cursor()

    for _, row in df.iterrows():
        cur.execute("""
            UPDATE score
            SET traffic_score = ?
            WHERE town_name = ?
        """, (float(row["traffic_score"]), row["town_name"]))

    # traffic_score → bus_score にコピー
    cur.execute("""
        UPDATE score
        SET bus_score = traffic_score
    """)

    conn.commit()
    conn.close()

    print("✔ traffic_score を統合しました")


# -----------------------------
# メイン処理
# -----------------------------
if __name__ == "__main__":
    print("=== セットアップ開始 ===")

    setup_town_db()
    setup_score_db()
    insert_town_names()
    write_area()
    write_hazard_score()
    write_traffic_score()

    print("=== セットアップ完了 ===")
