import sqlite3
import pandas as pd

def calculate_hazard_score():
    conn = sqlite3.connect("data/town.db")

    hazard = pd.read_sql("""
        SELECT town_name, hazard_flood, hazard_landslide, hazard_tsunami
        FROM hazard
    """, conn)

    conn.close()

    hazard["hazard_score"] = (
        hazard["hazard_flood"] * 0.4 +
        hazard["hazard_landslide"] * 0.3 +
        hazard["hazard_tsunami"] * 0.3
    )

    return hazard[["town_name", "hazard_score"]]
