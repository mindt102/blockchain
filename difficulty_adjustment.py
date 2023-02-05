import sqlite3

import pandas as pd

from utils import bits_to_target


def get_bits():
    db_name = "./data/bc.db"
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    query = "SELECT height, bits, timestamp FROM block_headers GROUP BY bits ORDER BY height ASC"
    cursor.execute(query)
    conn.commit()
    return cursor.fetchall()


df = pd.DataFrame(get_bits(), columns=["height", "bits", "timestamp"])
df["target"] = df["bits"].apply(bits_to_target)

periods = pd.DataFrame()
periods["time"] = df["timestamp"].diff().dropna() / 60
periods["blocks_per_min"] = 50 / periods["time"]
periods["difficulty"] = (df["target"][0] / df["target"]).shift(1)
periods["blocks"] = (df["height"] - 50).apply(str) + \
    "-" + (df["height"] - 1).apply(str)

print(periods)
