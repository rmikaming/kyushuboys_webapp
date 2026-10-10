import sqlite3

# town.db のパス（あなたの環境に合わせて固定）
DB_PATH = r"C:\Users\star_\OneDrive\Desktop\git作業用\テスト１\kyushuboys_webapp\data\town.db"

def add_hazard_columns():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 追加したいカラム一覧
    columns = [
        ("hazard_flood", "REAL"),
        ("hazard_landslide", "REAL"),
        ("hazard_quake", "REAL"),
        ("hazard_score", "REAL")
    ]

    # 既存カラムを確認
    cur.execute("PRAGMA table_info(towns)")
    existing_columns = {row[1] for row in cur.fetchall()}

    # 必要なカラムだけ追加
    for col_name, col_type in columns:
        if col_name not in existing_columns:
            print(f"Adding column: {col_name}")
            cur.execute(f"ALTER TABLE towns ADD COLUMN {col_name} {col_type}")
        else:
            print(f"Column already exists: {col_name}")

    conn.commit()
    conn.close()
    print("towns テーブルの hazard_* カラム追加が完了しました。")

if __name__ == "__main__":
    add_hazard_columns()
