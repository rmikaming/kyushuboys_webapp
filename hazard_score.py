import geopandas as gpd
import pandas as pd
import os

# ------------------------------------------------------------
# 1. SHPファイル探索（hazard_data配下の階層構造に対応）
# ------------------------------------------------------------
def find_shp(base_dir, keywords):
    """hazard_data以下からキーワードを含む.shpファイルを探す"""
    for root, dirs, files in os.walk(base_dir):
        for f in files:
            if f.endswith(".shp") and any(k in f or k in root for k in keywords):
                return os.path.join(root, f)
    return None


# ------------------------------------------------------------
# 2. ハザードデータ読み込み
# ------------------------------------------------------------
def load_hazard_layers():
    base_dir = "hazard_data"

    flood_mesh_path = find_shp(base_dir, ["flood_mesh", "10_計画規模"])
    flood_river_path = find_shp(base_dir, ["flood_river", "10_計画規模"])
    landslide_path = find_shp(base_dir, ["landslide"])
    tsunami_path = find_shp(base_dir, ["tsunami"])

    print("📍 flood_mesh:", flood_mesh_path)
    print("📍 flood_river:", flood_river_path)
    print("📍 landslide:", landslide_path)
    print("📍 tsunami:", tsunami_path)

    layers = {}
    for name, path in {
        "flood_mesh": flood_mesh_path,
        "flood_river": flood_river_path,
        "landslide": landslide_path,
        "tsunami": tsunami_path,
    }.items():
        if path:
            gdf = gpd.read_file(path)
            gdf = gdf.to_crs(epsg=4326)
            layers[name] = gdf
            print(f"✔ {name} 読み込み完了 ({len(gdf)} features)")
        else:
            print(f"⚠ {name} が見つかりません")

    return layers


# ------------------------------------------------------------
# 3. 町界データ読み込み
# ------------------------------------------------------------
def load_town_polygons():
    town_gdf = gpd.read_file("isahaya_town.geojson")
    town_gdf = town_gdf.to_crs(epsg=4326)
    town_gdf = town_gdf.rename(columns={"S_NAME": "town_name"})
    return town_gdf[["town_name", "geometry"]]


# ------------------------------------------------------------
# 4. ハザードスコア計算
# ------------------------------------------------------------
def calculate_hazard_score():
    town_gdf = load_town_polygons()
    layers = load_hazard_layers()

    # 各ハザードの町界内面積割合を計算
    scores = pd.DataFrame({"town_name": town_gdf["town_name"]})

    for name, gdf in layers.items():
        if gdf.empty:
            scores[name] = 0
            continue

        joined = gpd.overlay(town_gdf, gdf, how="intersection")
        joined["area"] = joined.geometry.area
        area_df = joined.groupby("town_name")["area"].sum().reset_index()

        town_gdf["area_total"] = town_gdf.geometry.area
        merged = pd.merge(town_gdf, area_df, on="town_name", how="left").fillna(0)
        merged[f"{name}_ratio"] = merged["area"] / merged["area_total"]

        scores = pd.merge(scores, merged[["town_name", f"{name}_ratio"]], on="town_name", how="left")

    # 各ハザードの平均を hazard_score として統合
    ratio_cols = [c for c in scores.columns if c.endswith("_ratio")]
    scores["hazard_score"] = scores[ratio_cols].mean(axis=1)

    scores["hazard_score"] = scores["hazard_score"].fillna(0)
    return scores[["town_name", "hazard_score"]]


# ------------------------------------------------------------
# 5. 実行確認
# ------------------------------------------------------------
if __name__ == "__main__":
    df = calculate_hazard_score()
    print(df.head())
    print("✔ hazard_score 計算完了")
