import sqlite3
import pandas as pd
from database import DB_PATH

conn = sqlite3.connect(DB_PATH)
#conn = sqlite3.connect("town.db")
df = pd.read_sql("SELECT * FROM score", conn)

#各要素の面積ごとの数（密度）を定義
df["hospital_density"] = df["hospital_count"] / df["area"]
df["school_density"] = df["school_count"] / df["area"]
df["crime_density"] = df["crime_count"] / df["area"]
df["bus_density"] = df["bus_stop_count"] / df["area"]

#偏差値導出の関数
def deviation(column):
    return 50 + 10 * (column - column.mean()) / column.std()

#各要素の偏差値（犯罪数は高いほど悪いので大小を逆転）
df["hospital_score"] = deviation(df["hospital_density"])
df["school_score"] = deviation(df["school_density"])
df["crime_score"] = 100 - deviation(df["crime_density"])
df["hazard_score"] = deviation(df["hazard_level"])
df["bus_score"] = deviation(df["bus_density"])

#town_nameと要素を選択して偏差値をアウトプット
def get_score(town_name, score_name):
    row = df[df["town_name"] == town_name]
    if row.empty:
        return None
    return row[score_name].iloc[0]

#全town_nameをリスト化
def get_town_list():
    return df["town_name"].tolist()