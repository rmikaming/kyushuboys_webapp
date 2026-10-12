import pandas as pd
import geopandas as gpd

BUS_STOP_FILE = "bus_stop_raw.txt"
TOWN_GEOJSON = "isahaya_town.geojson"


def load_town_polygons():
    town_gdf = gpd.read_file(TOWN_GEOJSON)
    town_gdf = town_gdf.to_crs(epsg=4326)
    town_gdf = town_gdf.rename(columns={"S_NAME": "town_name"})
    return town_gdf[["town_name", "geometry"]]


def load_bus_stops():
    df = pd.read_csv(BUS_STOP_FILE)

    # 列名を付け直す（あなたのデータ専用）
    df.columns = [
        "stop_id", "col1", "stop_name", "type",
        "lat", "lon",
        "col2", "col3", "col4", "col5", "col6", "col7", "col8", "col9"
    ]

    # 緯度・経度を float に変換
    df["lat"] = df["lat"].astype(float)
    df["lon"] = df["lon"].astype(float)

    # GeoDataFrame 化
    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df["lon"], df["lat"]),
        crs="EPSG:4326"
    )
    return gdf


def calculate_traffic_score():
    town_gdf = load_town_polygons()
    stops_gdf = load_bus_stops()

    joined = gpd.sjoin(stops_gdf, town_gdf, how="inner", predicate="within")
    stop_count_df = joined.groupby("town_name").size().reset_index(name="bus_stop_count")

    max_count = stop_count_df["bus_stop_count"].max()
    stop_count_df["traffic_score"] = stop_count_df["bus_stop_count"] / max_count

    return stop_count_df[["town_name", "traffic_score"]]
