import geopandas as gpd
import pandas as pd
import sqlite3
import glob
import os

SCORE_DB = "data/score.db"

def load_flood_river():
    folder = "hazard_data/flood_river/10_計画規模"
    shp_files = glob.glob(os.path.join(folder, "A31a-*.shp"))
    gdf_list = [gpd.read_file(shp).to_crs("EPSG:4326") for shp in shp_files]
    return gpd.GeoDataFrame(pd.concat(gdf_list, ignore_index=True), crs="EPSG:4326")


def calculate_hazard_score():
<<<<<<< HEAD
    conn = sqlite3.connect("school.db")
    towns = pd.read_sql("SELECT town_name, lat, lon FROM school_town", conn)
    conn.close()
=======
>>>>>>> 7a09d79bc635037f95f35426ba7d13a620cef84a

    # 町界
    towns_gdf = gpd.read_file("isahaya_geo/r2ka42204.shp").to_crs("EPSG:4326")
    towns_gdf = towns_gdf.rename(columns={"S_NAME": "town_name"})
    towns_gdf["centroid"] = towns_gdf.geometry.centroid

    # ハザードレイヤ
    haz_flood_mesh = gpd.read_file("hazard_data/flood_mesh/10_計画規模/A31b-10-25_10_4929.shp").to_crs("EPSG:4326")
    haz_flood_river = load_flood_river()
    haz_landslide = gpd.read_file("hazard_data/landslide/A33-25_42Polygon.shp").to_crs("EPSG:4326")
    haz_tsunami = gpd.read_file("hazard_data/tsunami/A40-16_42.shp").to_crs("EPSG:4326")

    def check_hazard(point, layer):
        return layer.contains(point).any()

    towns_gdf["haz_flood_mesh"] = towns_gdf["centroid"].apply(lambda p: check_hazard(p, haz_flood_mesh))
    towns_gdf["haz_flood_river"] = towns_gdf["centroid"].apply(lambda p: check_hazard(p, haz_flood_river))
    towns_gdf["haz_landslide"] = towns_gdf["centroid"].apply(lambda p: check_hazard(p, haz_landslide))
    towns_gdf["haz_tsunami"] = towns_gdf["centroid"].apply(lambda p: check_hazard(p, haz_tsunami))

    towns_gdf["hazard_score"] = (
        towns_gdf["haz_flood_mesh"].astype(int) * 0.3 +
        towns_gdf["haz_flood_river"].astype(int) * 0.3 +
        towns_gdf["haz_landslide"].astype(int) * 0.2 +
        towns_gdf["haz_tsunami"].astype(int) * 0.2
    )

    towns_gdf["hazard_score"] = towns_gdf["hazard_score"].fillna(0)

    return towns_gdf[["town_name", "hazard_score"]]


<<<<<<< HEAD
def write_hazard_score_to_sqlite(towns):
    conn = sqlite3.connect("school.db")
=======
def save_hazard_score_to_score_db():
    df = calculate_hazard_score()

    conn = sqlite3.connect(SCORE_DB)
>>>>>>> 7a09d79bc635037f95f35426ba7d13a620cef84a
    cur = conn.cursor()

    for _, row in df.iterrows():
        cur.execute("""
            UPDATE score
            SET hazard_score = ?
            WHERE town_name = ?
        """, (float(row["hazard_score"]), row["town_name"]))

    conn.commit()
    conn.close()


if __name__ == "__main__":
    save_hazard_score_to_score_db()
    print("🌋 hazard_score → score.db に保存完了")
