import sqlite3
from pathlib import Path

DB_PATH = Path("data/town.db")
#DB_PATH = Path("data/hospital.db")
#DBへの接続
def get_connection():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

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
    conn = get_connection()
    conn.execute("""
        INSERT INTO hospitals
        (name, address, created_at)
        VALUES (?, ?, ?)
    """, (
        hospital_data["name"],
        hospital_data["address"],
        hospital_data["created_at"]
    ))
    conn.commit()
    conn.close()

#DBのhospitalテーブルの中身を削除⇒リストの中身、hosupitals_dataを登録
def sync_hospitals(hospitals_data):
    delete_all_hospitals()

    for hospital_data in hospitals_data:
        insert_hospital(hospital_data)

