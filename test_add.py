import sqlite3
from database import DB_PATH

def integrate_scores():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 🔹 hazard_score を score に統合
    cur.execute("""
        UPDATE score
        SET hazard_score = (
            SELECT hazard_score
            FROM hazard
            WHERE hazard.town_name = score.town_name
        )
    """)

    # 🔹 traffic_score を score に統合
    # traffic_score を統合（traffic に無い町は 0 を返す）
    cur.execute("""
        UPDATE score
        SET traffic_score = COALESCE(
            (SELECT traffic_score FROM traffic
             WHERE traffic.town_name = score.town_name),
             0
        );
    """)


    conn.commit()
    conn.close()
    print("🎉 score テーブルへの hazard / traffic 統合が完了しました！")

if __name__ == "__main__":
    integrate_scores()
