import sqlite3

import matplotlib.pyplot as plt
import pandas as pd

from utils import bits_to_target

DB_NAME = "./data/bc.db"


def get_bits():
    print(f"Getting bits history from database {DB_NAME}...")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Get the bits history
    query = "SELECT height, bits, timestamp FROM block_headers WHERE mod(height, 50) = 0"
    cursor.execute(query)
    conn.commit()
    bits_history = cursor.fetchall()

    # Get the current bits
    query_current = "SELECT height, bits FROM block_headers ORDER BY height DESC LIMIT 1"
    bits_current = cursor.execute(query_current)
    conn.commit()
    bits_current = bits_current.fetchone()

    return bits_history, bits_current


history, current = get_bits()


df = pd.DataFrame(history, columns=["height", "bits", "timestamp"])
df["target"] = df["bits"].apply(bits_to_target)


periods = pd.DataFrame()
periods["time"] = df["timestamp"].diff().dropna() / 60
periods["blocks_per_min"] = 50 / periods["time"]
periods["difficulty"] = pd.to_numeric(
    (df["target"][0] / df["target"]).shift(1))
periods["blocks"] = (df["height"] - 50).apply(str) + \
    "-" + (df["height"] - 1).apply(str)
print(periods.round(2))
print()
print(
    f"Current difficulty: {df['target'][0] / bits_to_target(current[1])} at height {current[0]}")

# Select the first 20 periods
periods = periods.iloc[:20]

plt.bar(periods["blocks"], periods["difficulty"])
plt.xlabel("Block Periods")
plt.ylabel("Difficulty")
plt.xticks(rotation=45, ha='right', rotation_mode="anchor")
# plt.title("Difficulty of the first 20 periods (50 blocks each)")

plt.tight_layout()
plt.savefig("difficulty.png")

plt.clf()
plt.plot(periods["blocks"], periods["blocks_per_min"], color="red")
plt.xlabel("Block Periods")
plt.ylabel("Mining Rate (bpm)")
plt.xticks(rotation=45, ha='right', rotation_mode="anchor")

plt.axhline(y=1, color="black", linestyle="--")
plt.legend(["Mining Rate", "1 bpm"])

plt.tight_layout()
plt.savefig("mining_rate.png")
