import geopandas as gpd
import pandas as pd
import sqlite3
from shapely.geometry import Point
import glob
import os

def load_flood_river():
    folder = "hazard_data/flood_river/10_計画規模"
    shp_files = glob.glob(os.path.join(folder, "*.shp"))
    gdfs = [gpd.read_file(f).to_crs("EPSG:4326") for f in shp_files]
    return gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True))

def calculate_hazard_score():
    conn = sqlite3.connect("data/town.db")
    towns = pd.read_sql("SELECT town_name, lat, lon FROM town", conn)
    conn.close()

    flood_mesh  = gpd.read_file("hazard_data/flood_mesh/10_計画規模/A31b-10-25_10_4929.shp").to_crs("EPSG:4326")
    flood_river = load_flood_river()
    landslide   = gpd.read_file("hazard_data/landslide/A33-25_42Polygon.shp").to_crs("EPSG:4326")
    tsunami     = gpd.read_file("hazard_data/tsunami/A40-16_42.shp").to_crs("EPSG:4326")

    hazard_flood, hazard_landslide, hazard_quake = [], [], []

    for _, row in towns.iterrows():
        point = Point(row["lon"], row["lat"])
        flood_flag = flood_river.contains(point).any() or flood_mesh.contains(point).any()
        landslide_flag = landslide.contains(point).any()
        tsunami_flag = tsunami.contains(point).any()

        hazard_flood.append(1 if flood_flag else 0)
        hazard_landslide.append(1 if landslide_flag else 0)
        hazard_quake.append(1 if tsunami_flag else 0)

    towns["hazard_flood"] = hazard_flood
    towns["hazard_landslide"] = hazard_landslide
    towns["hazard_quake"] = hazard_quake
    towns["hazard_level"] = towns["hazard_flood"] + towns["hazard_landslide"] + towns["hazard_quake"]

    def deviation(col):
        return 50 + 10 * (col - col.mean()) / col.std()

    towns["hazard_score"] = deviation(towns["hazard_level"])
    return towns

# ★★★ score テーブルへ hazard_score を書き込む処理（追加） ★★★

def write_hazard_score_to_sqlite(towns):
    conn = sqlite3.connect("data/town.db")
    cur = conn.cursor()

    # カラムがなければ追加
    try:
        cur.execute("ALTER TABLE score ADD COLUMN hazard_score REAL;")
    except:
        pass

    # UPDATE で書き込み
    for _, row in towns.iterrows():
        cur.execute("""
            UPDATE score
            SET hazard_score = ?
            WHERE town_name = ?
        """, (float(row["hazard_score"]), row["town_name"]))

    conn.commit()
    conn.close()

# ---------- メイン処理 ----------

if __name__ == "__main__":
    print("=== hazard_score 生成開始 ===")

    towns = calculate_hazard_score()
    print(towns[["town_name", "hazard_score"]].head())

    write_hazard_score_to_sqlite(towns)
    print("hazard_score 書き込み完了")

    print("=== 完了 ===")


