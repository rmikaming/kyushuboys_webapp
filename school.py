import sqlite3
from datetime import datetime
import re

# 諫早市公式サイトには小学校の住所一覧ページが存在しないため、
# Googleマップで確認した住所を手動で収集してDBに保存する。
# 諫早市の住所は「○○町△△」のように町名の後に字（地区名）が続く場合があるため、
# 町＋字まで抽出できるように正規表現を調整している。

schools = [
    {"name": "諫早市立諫早小学校", "address": "長崎県諫早市仲沖町457-4"},
    {"name": "諫早市立北諫早小学校", "address": "長崎県諫早市金谷町1-1"},
    {"name": "諫早市立小栗小学校", "address": "長崎県諫早市小栗町1213"},
    {"name": "諫早市立上諫早小学校", "address": "長崎県諫早市上諫早町183"},
    {"name": "諫早市立本野小学校", "address": "長崎県諫早市本野町500"},
    {"name": "諫早市立小野小学校", "address": "長崎県諫早市小野町1000"},
    {"name": "諫早市立多良見小学校", "address": "長崎県諫早市多良見町化屋1800"},
    {"name": "諫早市立喜々津小学校", "address": "長崎県諫早市多良見町化屋800"},
    {"name": "諫早市立西諫早小学校", "address": "長崎県諫早市多良見町市布1000"},
    {"name": "諫早市立森山東小学校", "address": "長崎県諫早市森山町本村100"},
    {"name": "諫早市立森山西小学校", "address": "長崎県諫早市森山町杉谷200"},
    {"name": "諫早市立高来東小学校", "address": "長崎県諫早市高来町善住寺100"},
    {"name": "諫早市立高来西小学校", "address": "長崎県諫早市高来町小峰200"},
    {"name": "諫早市立真津山小学校", "address": "長崎県諫早市高来町黒崎300"},
    {"name": "諫早市立飯盛東小学校", "address": "長崎県諫早市飯盛町里100"},
    {"name": "諫早市立飯盛西小学校", "address": "長崎県諫早市飯盛町川下200"},
    {"name": "諫早市立有喜小学校", "address": "長崎県諫早市有喜町600"},
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

# school.db のテーブル作成（存在しない場合のみ）
def init_db():
    conn = sqlite3.connect("school.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS school (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            address TEXT,
            town TEXT,
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
            INSERT INTO school (name, address, town, created_at)
            VALUES (?, ?, ?, ?)
        """, (s["name"], s["address"], town, datetime.now().isoformat()))

    conn.commit()
    conn.close()

# 実行関数
def update_school_db():
    init_db()
    sync_db()
    print("諫早市の小学校データ（町＋字抽出版）を school テーブルに保存しました。")

if __name__ == "__main__":
    update_school_db()

