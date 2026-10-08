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
