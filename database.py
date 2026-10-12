import sqlite3
from pathlib import Path

DB_PATH = Path("data/town.db")

#DBへの接続
def get_connection():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

#addressにtownテーブルのtown_nameが含まれる場合townにtown_nameを代入
def find_town_name(address):
    conn = get_connection()

    #空のリストにtownテーブルのtown_nameを順番に加える
    towns = []
    town_names = conn.execute(
        "SELECT town_name FROM town"
    ).fetchall()
    for town_name in town_names:
        towns.append(town_name["town_name"])
    conn.close()

    #townsの中身を文字数が多い順番に並べ替える
    towns.sort(key=len, reverse=True)

    for town in towns:
        if town in address:
            return town

    return None

#hospital
#-------------------------------------------------------------------------------------------------------

#DBにhospitalテーブルがない場合作成（schema.sqlを実行）
def init_hospital_db():
    conn = get_connection()
    with open("schema.sql", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

#DBのhospitalテーブルの中身を削除
def delete_all_hospitals():
    conn = get_connection()
    conn.execute("DELETE FROM hospitals")
    conn.commit()
    conn.close()

#DBのhospitalテーブルにhospital_dataを登録
def insert_hospital(hospital_data):

    town_name = find_town_name(
        hospital_data["address"]
    )

    conn = get_connection()
    conn.execute("""
        INSERT INTO hospitals
        (name, address, town_name, created_at)
        VALUES (?, ?, ?, ?)
    """, (
        hospital_data["name"],
        hospital_data["address"],
        town_name,
        hospital_data["created_at"]
    ))
    conn.commit()
    conn.close()

#hospitalsのtown_nameとscoreのtown_nameが同じものをカウント⇒scoreのhospital_countを更新
def update_hospital_count():
    conn = get_connection()
    conn.execute("""
        UPDATE score
        SET hospital_count = (
            SELECT COUNT(*)
            FROM hospitals
            WHERE hospitals.town_name = score.town_name
            AND hospitals.name NOT LIKE '%薬局%'
        )
    """)
    conn.commit()
    conn.close()

#DBのhospitalテーブルの中身を削除⇒リストの中身、hosupitals_dataを登録⇒scoreのhospital_countを更新
def sync_hospitals(hospitals_data):
    delete_all_hospitals()

    for hospital_data in hospitals_data:
        insert_hospital(hospital_data)
    update_hospital_count()

#-------------------------------------------------------------------------------------------------------

#town
#-------------------------------------------------------------------------------------------------------

#DBのtownテーブルの中身を削除
def delete_all_score():
    conn = get_connection()
    conn.execute("DELETE FROM score")
    conn.commit()
    conn.close()

#DBのscoreテーブルにtownテーブルを登録
def insert_score_from_town():
    conn = get_connection()
    conn.execute("""
        INSERT INTO score(
        town_name,
        area,
        town_area_name
        )
        SELECT
            town_name,
            area,
            town_area_name
        FROM town
    """)
    conn.commit()
    conn.close()

def sync_score_from_town():
    delete_all_score()
    insert_score_from_town()
    update_hospital_count()


# crime（町別犯罪件数）
#-------------------------------------------------------------------------------------------------------
def update_crime_count_from_crime_stats():
    """
    crime.db の crime_stats.count を
    town.db の score.crime_count に反映する
    """

    conn_crime = sqlite3.connect("crime.db")
    conn_town = sqlite3.connect("data/town.db")

    cur_crime = conn_crime.cursor()
    cur_town = conn_town.cursor()

    # crime_stats の町名と件数を取得
    cur_crime.execute("SELECT town, count FROM crime_stats")
    rows = cur_crime.fetchall()

    # crime_count カラムがなければ追加
    cur_town.execute("PRAGMA table_info(score)")
    columns = [row[1] for row in cur_town.fetchall()]

    if "crime_count" not in columns:
        cur_town.execute("ALTER TABLE score ADD COLUMN crime_count INTEGER")
        print("crime_count カラムを追加しました")

    # crime_stats の件数を score に反映（NULL は 0 にする）
    for town_name, crime_count in rows:
        crime_count = crime_count if crime_count is not None else 0

        cur_town.execute("""
            UPDATE score
            SET crime_count = ?
            WHERE TRIM(town_name) = TRIM(?)
        """, (crime_count, town_name))

    # crime_stats に存在しない町は 0 にする
    cur_town.execute("""
        UPDATE score
        SET crime_count = 0
        WHERE crime_count IS NULL
    """)

    conn_town.commit()
    conn_crime.close()
    conn_town.close()

    print("crime_stats の count を town.db の score.crime_count に同期しました（NULL は 0 に変換）。")




#school.db　→　town.dbのscoreテーブルへ反映
#-------------------------------------------------------------------------------------------------------

import sqlite3

def update_school_count_from_score():
    """
    school.db の nearest_school.score を
    town.db の score.school_count に反映する
    """

    # school.db と town.db を開く
    conn_school = sqlite3.connect("school.db")
    conn_town = sqlite3.connect("data/town.db")

    cur_school = conn_school.cursor()
    cur_town = conn_town.cursor()

    # nearest_school の町名とスコアを取得
    cur_school.execute("SELECT town_name, score FROM nearest_school")
    rows = cur_school.fetchall()

    # town.db の score テーブルに school_count カラムがあるか確認
    cur_town.execute("PRAGMA table_info(score)")
    columns = [row[1] for row in cur_town.fetchall()]

    if "school_count" not in columns:
        cur_town.execute("ALTER TABLE score ADD COLUMN school_count REAL")
        print("town.db の score テーブルに school_count カラムを追加しました")

    # nearest_school の score を town.db.score.school_count に反映
    for town_name, score in rows:
        cur_town.execute("""
            UPDATE score
            SET school_count = ?
            WHERE TRIM(town_name) = TRIM(?)
        """, (score, town_name))

    conn_town.commit()
    conn_school.close()
    conn_town.close()

    print("nearest_school の score を town.db の score.school_count に保存しました。")

if __name__ == "__main__":
    update_school_count_from_score()
    update_crime_count_from_crime_stats()

def update_hazard_level_from_score():
    """
    score.db の score.hazard_score を
    town.db の score.hazard_level に反映する
    """

    # score.db と town.db を開く
    conn_score = sqlite3.connect("score.db")
    conn_town = sqlite3.connect("data/town.db")

    cur_score = conn_score.cursor()
    cur_town = conn_town.cursor()

    # score.db の hazard_score を取得
    cur_score.execute("SELECT town_name, hazard_score FROM score")
    rows = cur_score.fetchall()

    # town.db の score テーブルに hazard_level カラムがあるか確認
    cur_town.execute("PRAGMA table_info(score)")
    columns = [row[1] for row in cur_town.fetchall()]

    if "hazard_level" not in columns:
        cur_town.execute("ALTER TABLE score ADD COLUMN hazard_level REAL")
        print("town.db の score テーブルに hazard_level カラムを追加しました")

    # hazard_score → hazard_level に反映
    for town_name, hazard_score in rows:
        cur_town.execute("""
            UPDATE score
            SET hazard_level = ?
            WHERE TRIM(town_name) = TRIM(?)
        """, (hazard_score, town_name))

    conn_town.commit()
    conn_score.close()
    conn_town.close()

    print("score.db の hazard_score を town.db の score.hazard_level に保存しました。")

def update_bus_stop_count_from_score():
    """
    score.db の score.traffic_score を
    town.db の score.bus_stop_count に反映する
    """

    # score.db と town.db を開く
    conn_score = sqlite3.connect("score.db")
    conn_town = sqlite3.connect("data/town.db")

    cur_score = conn_score.cursor()
    cur_town = conn_town.cursor()

    # score.db の traffic_score を取得
    cur_score.execute("SELECT town_name, traffic_score FROM score")
    rows = cur_score.fetchall()

    # town.db の score テーブルに bus_stop_count カラムがあるか確認
    cur_town.execute("PRAGMA table_info(score)")
    columns = [row[1] for row in cur_town.fetchall()]

    if "bus_stop_count" not in columns:
        cur_town.execute("ALTER TABLE score ADD COLUMN bus_stop_count REAL")
        print("town.db の score テーブルに bus_stop_count カラムを追加しました")

    # traffic_score → bus_stop_count に反映
    for town_name, traffic_score in rows:
        cur_town.execute("""
            UPDATE score
            SET bus_stop_count = ?
            WHERE TRIM(town_name) = TRIM(?)
        """, (traffic_score, town_name))

    conn_town.commit()
    conn_score.close()
    conn_town.close()

    print("score.db の traffic_score を town.db の score.bus_stop_count に保存しました。")
