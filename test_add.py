import sqlite3
from hazard_score import calculate_hazard_score
from traffic_score import calculate_traffic_score

# hazard_score を score.db に統合
def write_hazard_score():
    hazard_df = calculate_hazard_score()

    conn = sqlite3.connect("data/score.db")
    cur = conn.cursor()

    for _, row in hazard_df.iterrows():
        cur.execute("""
            UPDATE score
            SET hazard_score = ?
            WHERE town_name = ?
        """, (float(row["hazard_score"]), row["town_name"]))

    conn.commit()
    conn.close()

# traffic_score を score.db に統合
def write_traffic_score():
    traffic_df = calculate_traffic_score()

    conn = sqlite3.connect("data/score.db")
    cur = conn.cursor()

    for _, row in traffic_df.iterrows():
        cur.execute("""
            UPDATE score
            SET traffic_score = ?
            WHERE town_name = ?
        """, (float(row["traffic_score"]), row["town_name"]))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    print("=== hazard_score 統合開始 ===")
    write_hazard_score()
    print("✔ hazard_score 統合完了")

    print("=== traffic_score 統合開始 ===")
    write_traffic_score()
    print("✔ traffic_score 統合完了")

    print("=== 完了 ===")
